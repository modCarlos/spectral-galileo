
import pandas as pd
import numpy as np

def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, slow=26, fast=12, signal=9):
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(data, window=20, num_std=2):
    sma = data['Close'].rolling(window=window).mean()
    std = data['Close'].rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, lower_band

def calculate_atr(data, window=14):
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    
    return true_range.rolling(window=window).mean()

def calculate_stochastic(data, window=14, smooth_window=3):
    """
    Calcula el Oscilador Estocástico (K y D).
    """
    low_min = data['Low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    
    k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=smooth_window).mean()
    
    return k_percent, d_percent

def calculate_obv(df):
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def calculate_mfi(df, window=14):
    """
    Money Flow Index - Indicador de momentum basado en volumen
    
    Combina precio y volumen. Similar a RSI pero considera volumen.
    MFI > 80: Sobrecomprado
    MFI < 20: Sobrevendido
    """
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    money_flow = typical_price * df['Volume']
    
    # Crear listas para flujo positivo y negativo
    positive_flow = []
    negative_flow = []
    
    # Primera entrada es 0
    positive_flow.append(0)
    negative_flow.append(0)
    
    for i in range(1, len(df)):
        if typical_price.iloc[i] > typical_price.iloc[i-1]:
            positive_flow.append(money_flow.iloc[i])
            negative_flow.append(0)
        elif typical_price.iloc[i] < typical_price.iloc[i-1]:
            positive_flow.append(0)
            negative_flow.append(money_flow.iloc[i])
        else:
            positive_flow.append(0)
            negative_flow.append(0)
    
    positive_mf = pd.Series(positive_flow, index=df.index).rolling(window).sum()
    negative_mf = pd.Series(negative_flow, index=df.index).rolling(window).sum()
    
    # Evitar división por cero
    mfi = 100 - (100 / (1 + (positive_mf / negative_mf.replace(0, 0.0001))))
    return mfi

def calculate_historical_volatility(df, window=20):
    """
    Volatilidad Histórica - Desviación estándar de retornos
    """
    returns = df['Close'].pct_change()
    volatility = returns.rolling(window).std() * np.sqrt(252)  # Anualizada
    return volatility

def calculate_adx(df, window=14):
    """
    Average Directional Index (ADX)
    Mide la fuerza de la tendencia (0-100).
    ADX > 25: Tendencia fuerte
    ADX < 20: Sin tendencia / Lateral
    """
    plus_dm = df['High'].diff()
    minus_dm = df['Low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    tr = calculate_atr(df, window=1) # Usamos TR de cada vela
    
    plus_di = 100 * (plus_dm.rolling(window).mean() / tr.rolling(window).mean())
    minus_di = 100 * (np.abs(minus_dm.rolling(window).mean()) / tr.rolling(window).mean())
    dx = 100 * (np.abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window).mean()
    
    return adx

def calculate_sma_slope(data, window=5):
    """
    Calcula la pendiente de la media móvil para detectar aplanamiento.
    Retorna el cambio porcentual de la SMA en N periodos.
    """
    sma = data.rolling(window=20).mean() # SMA base para el slope
    slope = (sma - sma.shift(window)) / sma.shift(window) * 100
    return slope

def detect_rsi_divergence(df, window=20):
    """
    Detecta divergencias simples entre precio y RSI.
    Divergencia Bajista: Precio hace máximos mayores, RSI hace máximos menores.
    """
    if len(df) < window: return False
    
    recent = df.iloc[-window:]
    
    # Encontrar índices de máximos locales de precio
    price_peaks = []
    for i in range(1, len(recent)-1):
        if recent['Close'].iloc[i] > recent['Close'].iloc[i-1] and \
           recent['Close'].iloc[i] > recent['Close'].iloc[i+1]:
            price_peaks.append(i)
            
    if len(price_peaks) < 2: return False
    
    # Comparar los dos últimos máximos
    p1, p2 = price_peaks[-2], price_peaks[-1]
    
    price_rising = recent['Close'].iloc[p2] > recent['Close'].iloc[p1]
    rsi_falling = recent['RSI'].iloc[p2] < recent['RSI'].iloc[p1]
    
    return price_rising and rsi_falling

def add_all_indicators(df):
    """
    Agrega todos los indicadores al DataFrame inplace.
    """
    df['SMA_50'] = calculate_sma(df, 50)
    df['SMA_200'] = calculate_sma(df, 200)
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df)
    df['BB_Upper'], df['BB_Lower'] = calculate_bollinger_bands(df)
    df['ATR'] = calculate_atr(df)
    stoch_k, stoch_d = calculate_stochastic(df)
    df['Stoch_K'] = stoch_k
    df['Stoch_D'] = stoch_d
    
    df['OBV'] = calculate_obv(df)
    
    # Nuevos indicadores
    df['MFI'] = calculate_mfi(df, window=14)
    df['HistVol'] = calculate_historical_volatility(df, window=20)
    df['ADX'] = calculate_adx(df)
    df['SMA_Slope'] = calculate_sma_slope(df['Close'])
    
    return df
