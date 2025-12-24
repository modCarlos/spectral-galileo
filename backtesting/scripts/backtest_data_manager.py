"""
Backtest Data Manager - Gestiona datos históricos locales para backtesting

Funcionalidad:
- Descarga datos históricos de yfinance
- Guarda datos en CSV local (backtest_data/)
- Lee datos desde CSV local (rápido)
- Actualiza datos diarios (append-only)
- Valida integridad de datos

Author: Spectral Galileo
Date: 2025-12-23
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BacktestDataManager:
    """
    Gestor de datos históricos para backtesting.
    
    Maneja descarga, almacenamiento y actualización de datos de precios.
    """
    
    def __init__(self, data_dir: str = "./backtest_data"):
        """
        Inicializa el gestor de datos.
        
        Args:
            data_dir: Directorio donde almacenar archivos CSV
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BacktestDataManager inicializado en: {self.data_dir}")
    
    def _get_csv_path(self, ticker: str) -> Path:
        """Obtiene la ruta del archivo CSV para un ticker."""
        return self.data_dir / f"{ticker.upper()}.csv"
    
    def download_historical(
        self, 
        ticker: str, 
        years: int = 5, 
        start_date: str = None, 
        end_date: str = None,
        force: bool = False
    ) -> pd.DataFrame:
        """
        Descarga datos históricos y los guarda en CSV.
        
        Si el archivo ya existe, lo reutiliza (a menos que force=True).
        
        Args:
            ticker: Símbolo del ticker (ej: 'AAPL')
            years: Años hacia atrás a descargar (default 1)
            start_date: Fecha inicio (formato YYYY-MM-DD). Sobrescribe 'years'
            end_date: Fecha fin (formato YYYY-MM-DD). Default: hoy
            force: Si True, fuerza descarga incluso si existe CSV
            
        Returns:
            DataFrame con datos OHLCV
        """
        csv_path = self._get_csv_path(ticker)
        
        # Si existe y no es force, retorna datos locales
        if csv_path.exists() and not force:
            logger.info(f"✓ {ticker}: Datos locales encontrados (sin descargar)")
            return self._read_csv(ticker)
        
        # Calcular fechas
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=365 * years)
            start_date = start_datetime.strftime('%Y-%m-%d')
        
        logger.info(f"Descargando {ticker} desde {start_date} hasta {end_date}...")
        
        try:
            # Descargar desde yfinance
            data = yf.download(
                ticker, 
                start=start_date, 
                end=end_date,
                progress=False
            )
            
            if data.empty:
                logger.warning(f"⚠ {ticker}: No se obtuvieron datos")
                return pd.DataFrame()
            
            # Si yfinance retorna MultiIndex en columnas, limpiar
            if isinstance(data.columns, pd.MultiIndex):
                # Aplanar las columnas usando el último nivel (el nombre real de la columna)
                data.columns = [col[-1] if isinstance(col, tuple) else col for col in data.columns]
            
            # Renombrar columnas estándar
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Asegurar que el índice sea DateTime
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            
            # Renombrar índice a 'Date'
            data.index.name = 'Date'
            
            # Ordenar por fecha
            data = data.sort_index()
            
            # Guardar a CSV
            data.to_csv(csv_path)
            logger.info(f"✓ {ticker}: {len(data)} días descargados y guardados en {csv_path}")
            
            return data
            
        except Exception as e:
            logger.error(f"✗ {ticker}: Error descargando - {str(e)}")
            return pd.DataFrame()
    
    def update_daily(self, ticker: str) -> bool:
        """
        Actualiza datos con el último cierre del mercado (append-only).
        
        Solo agrega la última fila si no existe en el CSV.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            True si se actualizó, False si no hay cambios o error
        """
        csv_path = self._get_csv_path(ticker)
        
        if not csv_path.exists():
            logger.warning(f"⚠ {ticker}: Archivo CSV no existe. Descargando primero...")
            self.download_historical(ticker, years=5)
            return True
        
        try:
            # Leer último dato guardado
            existing_data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
            last_saved_date = existing_data.index[-1]
            
            # Descargar solo últimos 2 días (para capturar cambios)
            start_date = (last_saved_date - timedelta(days=2)).strftime('%Y-%m-%d')
            new_data = yf.download(
                ticker, 
                start=start_date,
                progress=False
            )
            
            if new_data.empty:
                logger.info(f"ℹ {ticker}: Sin datos nuevos")
                return False
            
            # Buscar datos nuevos (después de last_saved_date)
            new_rows = new_data[new_data.index > last_saved_date]
            
            if new_rows.empty:
                logger.info(f"ℹ {ticker}: Ya actualizado")
                return False
            
            # Append a los datos existentes
            updated_data = pd.concat([existing_data, new_rows])
            updated_data = updated_data[~updated_data.index.duplicated(keep='last')]
            updated_data = updated_data.sort_index()
            
            # Guardar
            updated_data.to_csv(csv_path)
            logger.info(f"✓ {ticker}: Actualizado con {len(new_rows)} nuevo(s) día(s)")
            return True
            
        except Exception as e:
            logger.error(f"✗ {ticker}: Error actualizando - {str(e)}")
            return False
    
    def get_historical_range(
        self, 
        ticker: str, 
        start_date: str = None, 
        end_date: str = None,
        auto_download: bool = True
    ) -> pd.DataFrame:
        """
        Obtiene datos históricos de un rango de fechas.
        
        Intenta leer del CSV local. Si no existe y auto_download=True, descarga primero.
        
        Args:
            ticker: Símbolo del ticker
            start_date: Fecha inicio (formato YYYY-MM-DD)
            end_date: Fecha fin (formato YYYY-MM-DD)
            auto_download: Si True, descarga si no existe CSV local
            
        Returns:
            DataFrame con datos filtrados
        """
        csv_path = self._get_csv_path(ticker)
        
        # Si no existe, descargar
        if not csv_path.exists():
            if auto_download:
                logger.info(f"Datos de {ticker} no encontrados. Descargando...")
                data = self.download_historical(ticker, years=5)
            else:
                logger.warning(f"✗ {ticker}: Datos no encontrados y auto_download=False")
                return pd.DataFrame()
        else:
            # Leer del CSV
            data = self._read_csv(ticker)
        
        if data.empty:
            return data
        
        # Filtrar por rango de fechas si se especifica
        if start_date:
            data = data[data.index >= pd.to_datetime(start_date)]
        if end_date:
            data = data[data.index <= pd.to_datetime(end_date)]
        
        return data
    
    def _read_csv(self, ticker: str) -> pd.DataFrame:
        """
        Lee datos desde CSV local.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            DataFrame con datos
        """
        csv_path = self._get_csv_path(ticker)
        
        try:
            data = pd.read_csv(csv_path, index_col=0, parse_dates=[0])
            if data.index.name != 'Date':
                data.index.name = 'Date'
            return data
        except Exception as e:
            logger.error(f"✗ {ticker}: Error leyendo CSV - {str(e)}")
            return pd.DataFrame()
    
    def list_available_tickers(self) -> list:
        """
        Lista todos los tickers con datos descargados.
        
        Returns:
            Lista de tickers
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        tickers = [f.stem.upper() for f in csv_files]
        return sorted(tickers)
    
    def get_ticker_info(self, ticker: str) -> dict:
        """
        Obtiene información sobre los datos de un ticker.
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Dict con info (días, fechas, tamaño)
        """
        csv_path = self._get_csv_path(ticker)
        
        if not csv_path.exists():
            return {"status": "not_found", "ticker": ticker}
        
        try:
            data = self._read_csv(ticker)
            
            if data.empty:
                return {"status": "empty", "ticker": ticker}
            
            file_size_kb = csv_path.stat().st_size / 1024
            
            return {
                "status": "ok",
                "ticker": ticker,
                "days": len(data),
                "start_date": data.index[0].strftime('%Y-%m-%d'),
                "end_date": data.index[-1].strftime('%Y-%m-%d'),
                "file_size_kb": round(file_size_kb, 2),
                "columns": list(data.columns)
            }
        except Exception as e:
            return {
                "status": "error",
                "ticker": ticker,
                "error": str(e)
            }
    
    def bulk_download(
        self,
        tickers: list,
        years: int = 5,
        force: bool = False,
        max_workers: int = 4
    ) -> dict:
        """
        Descarga datos para múltiples tickers en paralelo.
        
        Args:
            tickers: Lista de símbolos
            years: Años hacia atrás
            force: Forzar descarga incluso si existen
            max_workers: Workers para descarga paralela (no implementado aún)
            
        Returns:
            Dict con resultados
        """
        results = {}
        logger.info(f"Iniciando descarga de {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                data = self.download_historical(ticker, years=years, force=force)
                results[ticker] = {
                    "status": "ok" if not data.empty else "no_data",
                    "rows": len(data)
                }
            except Exception as e:
                results[ticker] = {"status": "error", "error": str(e)}
        
        logger.info(f"✓ Descarga completada: {len([r for r in results.values() if r['status'] == 'ok'])}/{len(tickers)} exitosos")
        return results
    
    def validate_data(self, ticker: str, check_gaps: bool = True) -> dict:
        """
        Valida integridad de datos de un ticker.
        
        Args:
            ticker: Símbolo del ticker
            check_gaps: Si True, busca gaps de datos
            
        Returns:
            Dict con validación
        """
        csv_path = self._get_csv_path(ticker)
        
        if not csv_path.exists():
            return {"valid": False, "reason": "File not found"}
        
        try:
            data = self._read_csv(ticker)
            
            if data.empty:
                return {"valid": False, "reason": "Empty dataframe"}
            
            # Validar columnas
            required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}
            actual_cols = set(data.columns)
            
            if not required_cols.issubset(actual_cols):
                missing = required_cols - actual_cols
                return {"valid": False, "reason": f"Missing columns: {missing}"}
            
            # Validar datos numéricos
            for col in required_cols:
                if data[col].isna().any():
                    return {"valid": False, "reason": f"NaN values in {col}"}
            
            # Validar gaps de fechas (si aplica)
            result = {
                "valid": True,
                "ticker": ticker,
                "rows": len(data),
                "date_range": f"{data.index[0].date()} to {data.index[-1].date()}"
            }
            
            if check_gaps:
                # Calcular gaps
                date_diffs = data.index.to_series().diff()
                max_gap = date_diffs.max()
                
                # Gaps > 2 días podrían indicar problemas
                if max_gap > timedelta(days=2):
                    result["warning"] = f"Large gap detected: {max_gap}"
            
            return result
            
        except Exception as e:
            return {"valid": False, "reason": str(e)}


# CLI Interface
if __name__ == "__main__":
    import sys
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="Backtest Data Manager - Gestiona datos históricos")
    parser.add_argument("--download", nargs="+", help="Descargar datos para tickers")
    parser.add_argument("--update", nargs="+", help="Actualizar datos diarios para tickers")
    parser.add_argument("--list", action="store_true", help="Listar tickers disponibles")
    parser.add_argument("--info", help="Información de un ticker")
    parser.add_argument("--validate", help="Validar datos de un ticker")
    parser.add_argument("--years", type=int, default=5, help="Años a descargar (default 5 - largo plazo)")
    parser.add_argument("--force", action="store_true", help="Forzar descarga")
    parser.add_argument("--dir", default="./backtest_data", help="Directorio de datos")
    
    args = parser.parse_args()
    
    manager = BacktestDataManager(args.dir)
    
    if args.download:
        print(f"\n📥 Descargando {len(args.download)} tickers...")
        results = manager.bulk_download(args.download, years=args.years, force=args.force)
        for ticker, result in results.items():
            status = "✓" if result['status'] == 'ok' else "✗"
            print(f"  {status} {ticker}: {result}")
    
    elif args.update:
        print(f"\n📤 Actualizando {len(args.update)} tickers...")
        for ticker in args.update:
            manager.update_daily(ticker)
    
    elif args.list:
        tickers = manager.list_available_tickers()
        print(f"\n📊 Tickers disponibles ({len(tickers)}):")
        for ticker in tickers:
            info = manager.get_ticker_info(ticker)
            if info['status'] == 'ok':
                print(f"  • {ticker}: {info['days']} días ({info['start_date']} - {info['end_date']}) - {info['file_size_kb']} KB")
    
    elif args.info:
        info = manager.get_ticker_info(args.info)
        print(f"\n📋 Información de {args.info}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    elif args.validate:
        result = manager.validate_data(args.validate)
        print(f"\n✓ Validación de {args.validate}:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    
    else:
        parser.print_help()
