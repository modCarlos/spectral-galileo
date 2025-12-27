
import pandas as pd
from src.spectral_galileo.analysis import indicators

def calculate_fear_greed_index(vix_price, gspc_rsi):
    """
    Calcula un índice sintético de Miedo y Codicia (0-100).
    0 = Miedo Extremo
    100 = Codicia Extrema
    """
    # 1. Componente VIX (Volatilidad)
    # VIX normal: ~20. >30 miedo, <15 complacencia/codicia.
    # Normalizamos VIX invirtiendo: Rango esperado 10 - 40 de forma laxa.
    # Si VIX=10 -> Score 100 (Codicia). Si VIX=40 -> Score 0 (Miedo).
    # Formula lineal simple: Score = 100 - ((VIX - 10) / 30 * 100)
    # Clampeamos entre 0 y 100.
    vix_score = 100 - ((vix_price - 10) / (35 - 10) * 100)
    vix_score = max(0, min(100, vix_score))

    # 2. Componente Momento (S&P 500 RSI)
    # RSI ya es 0-100.
    # RSI > 70 (Codicia), RSI < 30 (Miedo).
    momentum_score = gspc_rsi

    # Promedio ponderado (50/50)
    final_index = (vix_score * 0.5) + (momentum_score * 0.5)
    return final_index

def analyze_macro_context(df_macro):
    """
    Analiza el contexto macroeconómico global.
    Espera un DataFrame donde las columnas son los Tickers (^VIX, ^TNX, ^GSPC).
    """
    if df_macro is None or df_macro.empty:
        return {"error": "Sin datos macro"}

    latest = df_macro.iloc[-1]
    
    # Extraer valores recientes (manejando posible MultiIndex columns de yfinance en versiones nuevas)
    # Asumimos que df_macro['^VIX'] retorna Series.
    try:
        vix = latest['^VIX']
        tnx = latest['^TNX']
        gspc = latest['^GSPC']
        irx = latest.get('^IRX', 0)
    except KeyError:
        # Fallback por si la estructura de yfinance cambia (e.g. MultiIndex con 'Close')
        # En la implementation anterior de market_data pedimos ['Close'] explicitamente.
        # Si sigue fallando, retornamos basic error
        return {"error": "Error estructura datos macro"}

    # Yield Curve Spread (10Y - 13W)
    yield_spread = tnx - irx

    # Calcular RSI del S&P 500 para el Fear & Greed
    # Necesitamos la serie historica de GSPC
    gspc_series = df_macro['^GSPC'].to_frame(name='Close') # indicators espera DataFrame con 'Close'
    gspc_series['RSI'] = indicators.calculate_rsi(gspc_series)
    gspc_rsi = gspc_series.iloc[-1]['RSI']

    # Fear & Greed
    fgi = calculate_fear_greed_index(vix, gspc_rsi)
    
    if fgi < 25: fgi_label = "Miedo Extremo 😱"
    elif fgi < 45: fgi_label = "Miedo 😨"
    elif fgi < 55: fgi_label = "Neutral 😐"
    elif fgi < 75: fgi_label = "Codicia 🤑"
    else: fgi_label = "Codicia Extrema 🚀"

    # TNX Trend (Simple: Comparar con hace 20 dias)
    tnx_prev = df_macro.iloc[-20]['^TNX'] if len(df_macro) > 20 else tnx
    tnx_trend = "Subiendo" if tnx > tnx_prev * 1.05 else "Bajando" if tnx < tnx_prev * 0.95 else "Lateral"

    return {
        "vix": vix,
        "tnx": tnx,
        "irx": irx,
        "yield_spread": yield_spread,
        "tnx_trend": tnx_trend,
        "gspc_rsi": gspc_rsi,
        "fear_greed_index": fgi,
        "fear_greed_label": fgi_label
    }
