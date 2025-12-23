
import json
import os
import datetime
import market_data

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=4)

def add_stock(ticker, price=None):
    """
    Agrega una acción al portafolio.
    
    Args:
        ticker: Símbolo de la acción
        price: Precio de compra personalizado (opcional). Si no se provee, usa precio actual.
    """
    ticker = ticker.upper()
    
    # Si no se provee precio, obtener precio actual
    if price is None:
        try:
            t = market_data.get_ticker_data(ticker)
            data = market_data.get_historical_data(t, period="1d")
            buy_price = data['Close'].iloc[-1]
        except Exception as e:
            return f"Error al obtener datos para {ticker}: {str(e)}"
    else:
        try:
            buy_price = float(price)
            if buy_price <= 0:
                return "Error: El precio debe ser mayor a 0."
        except ValueError:
            return "Error: Precio inválido. Debe ser un número."

    portfolio = load_portfolio()
    
    entry = {
        "symbol": ticker,
        "buy_price": float(buy_price),
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    portfolio.append(entry)
    save_portfolio(portfolio)
    
    price_source = "actual del mercado" if price is None else "personalizado"
    return f"Acción {ticker} agregada al portafolio.\nPrecio de compra: ${buy_price:.2f} ({price_source})\nFecha: {entry['date']}"

def get_portfolio_tickers():
    portfolio = load_portfolio()
    # Retornar lista única de tickers
    return list(set([item['symbol'] for item in portfolio]))

def get_holdings(ticker):
    """Retorna todas las entradas para un ticker específico"""
    portfolio = load_portfolio()
    return [item for item in portfolio if item['symbol'] == ticker]

def remove_last_stock(ticker):
    """
    Elimina la última entrada de una acción del portafolio.
    """
    portfolio = load_portfolio()
    ticker = ticker.upper()
    
    # Buscar la última entrada (más reciente por fecha)
    matching = [i for i, item in enumerate(portfolio) if item['symbol'] == ticker]
    
    if not matching:
        return f"No se encontró {ticker} en el portafolio."
    
    # Eliminar el último índice encontrado
    removed = portfolio.pop(matching[-1])
    save_portfolio(portfolio)
    
    return f"Eliminada entrada de {ticker} (Precio: ${removed['buy_price']:.2f}, Fecha: {removed['date']})"

def remove_all_stock(ticker):
    """
    Elimina todas las entradas de una acción del portafolio.
    """
    portfolio = load_portfolio()
    ticker = ticker.upper()
    
    initial_count = len(portfolio)
    portfolio = [item for item in portfolio if item['symbol'] != ticker]
    
    removed_count = initial_count - len(portfolio)
    
    if removed_count == 0:
        return f"No se encontró {ticker} en el portafolio."
    
    save_portfolio(portfolio)
    return f"Eliminadas {removed_count} entrada(s) de {ticker} del portafolio."

def clear_portfolio():
    """
    Elimina todas las acciones del portafolio.
    """
    save_portfolio([])
    return "Portafolio vaciado completamente."
