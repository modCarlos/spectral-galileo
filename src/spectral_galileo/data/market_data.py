
import yfinance as yf
import pandas as pd

import sys
import os
import contextlib

def get_ticker_data(ticker_symbol):
    """
    Obtiene el objeto Ticker de yfinance.
    """
    return yf.Ticker(ticker_symbol)

def get_historical_data(ticker, period="1y", interval="1d"):
    """
    Obtiene datos históricos para análisis técnico.
    """
    with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
        history = ticker.history(period=period, interval=interval)
    
    if history.empty:
        raise ValueError(f"No se encontraron datos históricos para {ticker.ticker}")
    return history

def get_fundamental_info(ticker):
    """
    Extrae información fundamental relevante.
    Silencia stderr durante el acceso a .info por si acaso.
    """
    try:
        with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
            info = ticker.info
    except Exception:
        info = {}
        
    return {
        "symbol": info.get("symbol"),
        "shortName": info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "longBusinessSummary": info.get("longBusinessSummary"),  # Descripción del negocio
        
        # Valuación
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "pegRatio": info.get("pegRatio"),
        "priceToBook": info.get("priceToBook"),
        
        # Rentabilidad
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        "profitMargins": info.get("profitMargins"),
        
        # Ingresos y Ganancias
        "totalRevenue": info.get("totalRevenue"),
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
        
        # EPS
        "trailingEps": info.get("trailingEps"),
        "forwardEps": info.get("forwardEps"),
        
        # Deuda y Salud Financiera
        "debtToEquity": info.get("debtToEquity"),
        "currentRatio": info.get("currentRatio"),
        
        # Dividendos
        "dividendYield": info.get("dividendYield"),
        "dividendRate": info.get("dividendRate"),
        "payoutRatio": info.get("payoutRatio"),
        
        # Flujo de Caja
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        
        # Precio y Target
        "currentPrice": info.get("currentPrice"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "recommendationKey": info.get("recommendationKey"),
        
        # Riesgos y Gestión
        "beta": info.get("beta"),
        "companyOfficers": info.get("companyOfficers"), # Para calcular Tenure
        "heldPercentInsiders": info.get("heldPercentInsiders"),
        "marketCap": info.get("marketCap"),
        "averageVolume": info.get("averageVolume"),
        "averageVolume10days": info.get("averageVolume10days")
    }

def get_earnings_surprise(ticker):
    """
    Obtiene el promedio de sorpresas en beneficios (surprisePercent) de los últimos 4 quarters.
    """
    try:
        hist = ticker.earnings_history
        if hist is not None and not hist.empty:
            # Tomar los últimos 4 registros y promediar surprisePercent
            recent = hist.head(4)
            if 'surprisePercent' in recent.columns:
                return recent['surprisePercent'].mean()
    except Exception:
        pass
    return 0.0

def get_spy_correlation(ticker, days=60):
    """
    Calcula la correlación de N días entre el ticker y SPY.
    """
    try:
        # Descargar datos para SPY y el ticker
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=days*2) # Pedir más días por seguridad
        
        spy = yf.download("SPY", start=start_date, progress=False)['Close']
        tk_data = ticker.history(start=start_date)['Close']
        
        # Alinear series
        combined = pd.concat([spy, tk_data], axis=1).dropna()
        combined.columns = ['SPY', 'Ticker']
        
        if len(combined) < days: return 0.5 # Valor neutro si faltan datos
        
        return combined['Ticker'].corr(combined['SPY'])
    except Exception:
        return 0.5

def get_next_earnings_date(ticker):
    """
    Obtiene la próxima fecha de resultados del calendario.
    """
    try:
        cal = ticker.calendar
        if cal and 'Earnings Date' in cal and cal['Earnings Date']:
            return cal['Earnings Date'][0]
    except Exception:
        pass
    return None

def get_news(ticker):
    """
    Obtiene las noticias más recientes combinando yfinance y Google News RSS.
    """
    import requests
    from xml.etree import ElementTree
    
    news_list = []
    titles_seen = set()

    # 1. Fuente Primaria: yfinance (Formato nativo)
    try:
        with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
            yf_news = ticker.news
            for item in yf_news:
                title = item.get('title', '')
                if title:
                    news_list.append(item)
                    titles_seen.add(title.lower())
    except Exception:
        pass

    # 2. Fuente Secundaria: Google News RSS (Formato simulado)
    try:
        ticker_symbol = ticker.ticker
        rss_url = f"https://news.google.com/rss/search?q={ticker_symbol}+stock&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url, timeout=5)
        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            for item in root.findall('.//item')[:20]: # Tomar hasta 20 adicionales
                title = item.find('title').text
                link = item.find('link').text
                if title and title.lower() not in titles_seen:
                    news_list.append({
                        'title': title,
                        'link': link,
                        'publisher': 'Google News',
                        'providerPublishTime': 0 # No disponible exacto en RSS simple
                    })
                    titles_seen.add(title.lower())
    except Exception:
        pass

    return news_list

def get_peers(sector):
    """
    Retorna una lista de competidores populares basada en el sector.
    Esta es una lista estática simplificada para demostración.
    """
    sectors = {
        "Technology": ["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "AMZN"],
        "Financial Services": ["JPM", "BAC", "V", "MA", "GS"],
        "Healthcare": ["JNJ", "PFE", "UNH", "LLY", "ABBV"],
        "Consumer Cyclical": ["TSLA", "AMZN", "HD", "NKE", "MCD"],
        "Industrials": ["BA", "CAT", "GE", "HON", "UPS"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
        "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "T"]
    }
    
    # Búsqueda aproximada
    for key, peers in sectors.items():
        if sector and key in sector:
            return peers
            
    return []

def get_macro_data():
    """
    Obtiene datos macroeconómicos recientes (VIX, TNX, S&P500).
    """
    tickers = ["^VIX", "^TNX", "^GSPC", "^IRX"]
    try:
        # Descarga últimos 100 periodos para cálculos de media/RSI si fuera necesario
        with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
            data = yf.download(tickers, period="6mo", interval="1d", progress=False)['Close']
        return data
    except Exception as e:
        # Silenciar print de error también o dejarlo para debug? 
        # El user quiere bloquear errores como "Failed download", que salen de yfinance.
        # "Error fetching macro data" es nuestro print, ese lo podemos dejar o quitar si es verbose.
        return None

def get_sp500_top25():
    """
    Retorna la lista de las ~25 empresas más grandes del S&P 500.
    Lista estática actualizada manualmente (o se podría buscar dinámicamente).
    """
    return [
        "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", 
        "LLY", "AVGO", "JPM", "XOM", "UNH", "V", "PG", "MA", "COST", 
        "JNJ", "HD", "MRK", "ABBV", "KO", "BAC", "WMT", "CRM"
    ]
