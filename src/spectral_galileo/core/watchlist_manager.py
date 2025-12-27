
import json
import os

WATCHLIST_FILE = "config/watchlist.json"

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist, f, indent=4)

def add_to_watchlist(ticker):
    """
    Agrega un ticker a la watchlist si no existe.
    """
    ticker = ticker.upper().strip()
    watchlist = load_watchlist()
    
    if ticker in watchlist:
        return f"La acción {ticker} ya está en tu watchlist."
    
    watchlist.append(ticker)
    save_watchlist(watchlist)
    return f"Acción {ticker} agregada a la watchlist."

def remove_from_watchlist(ticker):
    """
    Elimina un ticker de la watchlist.
    """
    ticker = ticker.upper().strip()
    watchlist = load_watchlist()
    
    if ticker not in watchlist:
        return f"La acción {ticker} no está en tu watchlist."
    
    watchlist.remove(ticker)
    save_watchlist(watchlist)
    return f"Acción {ticker} eliminada de la watchlist."

def get_watchlist_tickers():
    """Retorna la lista de tickers en la watchlist."""
    return load_watchlist()

def clear_watchlist():
    """Vacía la watchlist."""
    save_watchlist([])
    return "Watchlist vaciada completamente."
