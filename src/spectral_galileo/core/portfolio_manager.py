
import json
import os
import datetime
from src.spectral_galileo.data import market_data

PORTFOLIO_FILE = "data/portfolio.json"
CONFIG_FILE = "config/portfolio_config.json"

def load_config():
    """Load portfolio configuration (account value, risk settings)"""
    if not os.path.exists(CONFIG_FILE):
        # Default configuration
        return {
            "account_value": 100000,
            "max_risk_per_trade": 0.02,
            "max_position_allocation": 0.20
        }
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "account_value": 100000,
            "max_risk_per_trade": 0.02,
            "max_position_allocation": 0.20
        }

def save_config(config):
    """Save portfolio configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_account_value():
    """Get current account value from config"""
    config = load_config()
    return config.get("account_value", 100000)

def set_account_value(value):
    """Set account value in config"""
    config = load_config()
    config["account_value"] = float(value)
    save_config(config)
    return f"Account value actualizado a ${value:,.2f}"

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

def add_stock(ticker, price=None, stop_loss=None, take_profit=None, position_size=None):
    """
    Agrega una acción al portafolio con información de Risk Management.
    
    Args:
        ticker: Símbolo de la acción
        price: Precio de compra personalizado (opcional). Si no se provee, usa precio actual.
        stop_loss: Precio de Stop Loss (opcional)
        take_profit: Precio de Take Profit (opcional)
        position_size: Número de acciones a comprar (opcional)
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
    
    # Phase 4B: Add Risk Management fields
    if stop_loss is not None:
        entry["stop_loss"] = float(stop_loss)
    if take_profit is not None:
        entry["take_profit"] = float(take_profit)
    if position_size is not None:
        entry["position_size"] = int(position_size)
    
    portfolio.append(entry)
    save_portfolio(portfolio)
    
    price_source = "actual del mercado" if price is None else "personalizado"
    msg = f"Acción {ticker} agregada al portafolio.\nPrecio de compra: ${buy_price:.2f} ({price_source})\nFecha: {entry['date']}"
    
    if stop_loss is not None:
        msg += f"\nStop Loss: ${stop_loss:.2f}"
    if take_profit is not None:
        msg += f"\nTake Profit: ${take_profit:.2f}"
    if position_size is not None:
        msg += f"\nPosición: {position_size} acciones"
    
    return msg

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

def check_stop_loss_take_profit():
    """
    Phase 4B: Monitorea diariamente el portafolio y valida si alguna posición
    alcanzó su Stop Loss o Take Profit.
    
    Returns:
        Dict con alertas de TP/SL alcanzados y recomendaciones.
    """
    portfolio = load_portfolio()
    alerts = {
        "stop_loss_hit": [],
        "take_profit_hit": [],
        "no_rm": [],  # Posiciones sin RM configurado
        "active": []  # Posiciones activas dentro de TP/SL
    }
    
    for entry in portfolio:
        ticker = entry["symbol"]
        buy_price = entry["buy_price"]
        
        # Obtener precio actual
        try:
            t = market_data.get_ticker_data(ticker)
            data = market_data.get_historical_data(t, period="1d")
            current_price = data['Close'].iloc[-1]
        except Exception as e:
            alerts["no_rm"].append({
                "ticker": ticker,
                "buy_price": buy_price,
                "error": f"No se pudo obtener precio actual: {str(e)}"
            })
            continue
        
        # Validar TP/SL si existen
        has_sl = "stop_loss" in entry
        has_tp = "take_profit" in entry
        
        if not has_sl and not has_tp:
            # Sin RM configurado
            pnl_pct = ((current_price - buy_price) / buy_price) * 100
            alerts["no_rm"].append({
                "ticker": ticker,
                "buy_price": buy_price,
                "current_price": current_price,
                "pnl_percent": pnl_pct,
                "recommendation": "Configurar Stop Loss y Take Profit"
            })
            continue
        
        # Validar Stop Loss
        if has_sl and current_price <= entry["stop_loss"]:
            pnl = current_price - buy_price
            pnl_pct = (pnl / buy_price) * 100
            alerts["stop_loss_hit"].append({
                "ticker": ticker,
                "buy_price": buy_price,
                "stop_loss": entry["stop_loss"],
                "current_price": current_price,
                "pnl": pnl,
                "pnl_percent": pnl_pct,
                "date": entry["date"],
                "position_size": entry.get("position_size"),
                "recommendation": f"VENDER {ticker} - Stop Loss alcanzado"
            })
            continue
        
        # Validar Take Profit
        if has_tp and current_price >= entry["take_profit"]:
            pnl = current_price - buy_price
            pnl_pct = (pnl / buy_price) * 100
            alerts["take_profit_hit"].append({
                "ticker": ticker,
                "buy_price": buy_price,
                "take_profit": entry["take_profit"],
                "current_price": current_price,
                "pnl": pnl,
                "pnl_percent": pnl_pct,
                "date": entry["date"],
                "position_size": entry.get("position_size"),
                "recommendation": f"VENDER {ticker} - Take Profit alcanzado"
            })
            continue
        
        # Posición activa
        pnl = current_price - buy_price
        pnl_pct = (pnl / buy_price) * 100
        
        sl_distance = ((entry["stop_loss"] - current_price) / current_price * 100) if has_sl else None
        tp_distance = ((entry["take_profit"] - current_price) / current_price * 100) if has_tp else None
        
        alerts["active"].append({
            "ticker": ticker,
            "buy_price": buy_price,
            "current_price": current_price,
            "stop_loss": entry.get("stop_loss"),
            "take_profit": entry.get("take_profit"),
            "pnl": pnl,
            "pnl_percent": pnl_pct,
            "sl_distance_pct": sl_distance,
            "tp_distance_pct": tp_distance,
            "position_size": entry.get("position_size")
        })
    
    return alerts

def format_rm_alerts(alerts):
    """
    Formatea las alertas de Risk Management para mostrar al usuario.
    """
    output = []
    
    # Stop Loss alcanzados
    if alerts["stop_loss_hit"]:
        output.append("\n🛑 STOP LOSS ALCANZADOS - ACCIÓN REQUERIDA:")
        output.append("=" * 60)
        for item in alerts["stop_loss_hit"]:
            output.append(f"\n{item['ticker']}:")
            output.append(f"  Precio Compra: ${item['buy_price']:.2f}")
            output.append(f"  Stop Loss: ${item['stop_loss']:.2f}")
            output.append(f"  Precio Actual: ${item['current_price']:.2f}")
            output.append(f"  P&L: ${item['pnl']:.2f} ({item['pnl_percent']:.2f}%)")
            if item['position_size']:
                total_loss = item['pnl'] * item['position_size']
                output.append(f"  Pérdida Total: ${total_loss:.2f} ({item['position_size']} acciones)")
            output.append(f"  ➡️  {item['recommendation']}")
    
    # Take Profit alcanzados
    if alerts["take_profit_hit"]:
        output.append("\n✅ TAKE PROFIT ALCANZADOS - ACCIÓN REQUERIDA:")
        output.append("=" * 60)
        for item in alerts["take_profit_hit"]:
            output.append(f"\n{item['ticker']}:")
            output.append(f"  Precio Compra: ${item['buy_price']:.2f}")
            output.append(f"  Take Profit: ${item['take_profit']:.2f}")
            output.append(f"  Precio Actual: ${item['current_price']:.2f}")
            output.append(f"  P&L: ${item['pnl']:.2f} (+{item['pnl_percent']:.2f}%)")
            if item['position_size']:
                total_profit = item['pnl'] * item['position_size']
                output.append(f"  Ganancia Total: ${total_profit:.2f} ({item['position_size']} acciones)")
            output.append(f"  ➡️  {item['recommendation']}")
    
    # Posiciones sin RM
    if alerts["no_rm"]:
        output.append("\n⚠️  POSICIONES SIN RISK MANAGEMENT:")
        output.append("=" * 60)
        for item in alerts["no_rm"]:
            if "error" in item:
                output.append(f"\n{item['ticker']}: {item['error']}")
            else:
                output.append(f"\n{item['ticker']}:")
                output.append(f"  Precio Compra: ${item['buy_price']:.2f}")
                output.append(f"  Precio Actual: ${item['current_price']:.2f}")
                output.append(f"  P&L: {item['pnl_percent']:.2f}%")
                output.append(f"  ➡️  {item['recommendation']}")
    
    # Posiciones activas
    if alerts["active"]:
        output.append("\n📊 POSICIONES ACTIVAS:")
        output.append("=" * 60)
        for item in alerts["active"]:
            output.append(f"\n{item['ticker']}:")
            output.append(f"  Precio Compra: ${item['buy_price']:.2f}")
            output.append(f"  Precio Actual: ${item['current_price']:.2f}")
            output.append(f"  P&L: ${item['pnl']:.2f} ({item['pnl_percent']:.2f}%)")
            if item['stop_loss']:
                output.append(f"  Stop Loss: ${item['stop_loss']:.2f} ({item['sl_distance_pct']:.2f}% distancia)")
            if item['take_profit']:
                output.append(f"  Take Profit: ${item['take_profit']:.2f} (+{item['tp_distance_pct']:.2f}% distancia)")
            if item['position_size']:
                total_value = item['current_price'] * item['position_size']
                output.append(f"  Posición: {item['position_size']} acciones (${total_value:.2f})")
    
    if not any([alerts["stop_loss_hit"], alerts["take_profit_hit"], alerts["no_rm"], alerts["active"]]):
        output.append("\n✅ Portafolio vacío o sin posiciones activas.")
    
    return "\n".join(output)
