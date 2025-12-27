"""
Módulo para gestionar la obtención de datos de forma eficiente,
usando concurrencia y caché simple.
"""

import concurrent.futures
from src.spectral_galileo.data import market_data
from datetime import datetime, timedelta

class DataManager:
    def __init__(self):
        self._macro_cache = None
        self._macro_timestamp = None
        self._ticker_cache = {} # Sencillo caché por sesión
    
    def get_ticker_data(self, ticker_symbol):
        """
        Obtiene todos los datos necesarios para un ticker en paralelo.
        """
        if ticker_symbol in self._ticker_cache:
            return self._ticker_cache[ticker_symbol]

        ticker_obj = market_data.get_ticker_data(ticker_symbol)
        
        # Usar hilos para descargar componentes en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_hist = executor.submit(market_data.get_historical_data, ticker_obj)
            future_fund = executor.submit(market_data.get_fundamental_info, ticker_obj)
            future_news = executor.submit(market_data.get_news, ticker_obj)
            
            try:
                history = future_hist.result(timeout=15)
                fundamentals = future_fund.result(timeout=15)
                news = future_news.result(timeout=15)
            except Exception as e:
                # Si falla uno, re-lanzamos o manejamos según importancia
                raise e
                
        data = {
            "ticker_obj": ticker_obj,
            "history": history,
            "fundamentals": fundamentals,
            "news": news
        }
        
        self._ticker_cache[ticker_symbol] = data
        return data

    def get_macro_data(self, force_refresh=False):
        """
        Obtiene datos macro con caché (válido por 1 hora por defecto).
        """
        now = datetime.now()
        if not force_refresh and self._macro_cache is not None:
            if self._macro_timestamp and (now - self._macro_timestamp) < timedelta(hours=1):
                return self._macro_cache
        
        data = market_data.get_macro_data()
        if data is not None:
            self._macro_cache = data
            self._macro_timestamp = now
            
        return data
