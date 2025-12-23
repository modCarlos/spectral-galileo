
from textblob import TextBlob

def analyze_sentiment(news_list):
    """
    Analiza una lista de diccionarios de noticias (formato yfinance).
    Retorna un score promedio de -1 (Muy negativo) a 1 (Muy positivo)
    y un conteo de positivas/negativas/neutras.
    """
    if not news_list:
        return 0, {"positive": 0, "neutral": 0, "negative": 0}

    total_polarity = 0
    counts = {"positive": 0, "neutral": 0, "negative": 0}

    for item in news_list:
        # Intentar obtener título de estructura plana o anidada
        title = item.get('title')
        if not title and 'content' in item:
            title = item['content'].get('title')
            
        if not title:
            continue
            
        analysis = TextBlob(title)
        polarity = analysis.sentiment.polarity
        total_polarity += polarity

        if polarity > 0.05:
            counts["positive"] += 1
        elif polarity < -0.05:
            counts["negative"] += 1
        else:
            counts["neutral"] += 1

    avg_polarity = total_polarity / len(news_list)
    return avg_polarity, counts

def advanced_sentiment_analysis(news_list):
    """
    Análisis avanzado de sentimiento con keywords y volumen
    
    Returns:
        {
            'score': float,
            'label': str,
            'volume': int,
            'critical_keywords': list,
            'volume_score': float
        }
    """
    # Keywords críticos
    CRITICAL_POSITIVE = ['breakthrough', 'record', 'expansion', 'growth', 
                        'profit', 'beat', 'exceeds', 'innovation', 'surge',
                        'milestone', 'award', 'partnership', 'approval']
    CRITICAL_NEGATIVE = ['lawsuit', 'regulation', 'crisis', 'decline', 
                        'loss', 'investigation', 'recall', 'warning', 'bankruptcy',
                        'scandal', 'fine', 'violation', 'downgrade']
    
    if not news_list:
        return {
            'score': 0,
            'label': 'Sin Datos',
            'volume': 0,
            'critical_keywords': [],
            'volume_score': 0
        }
    
    sentiments = []
    critical_kw = []
    
    total_news = len(news_list)
    # Procesamos todas las noticias disponibles (máximo 40 recomendado para performance)
    for i, article in enumerate(news_list[:40]):  
        # Extraer título
        if isinstance(article, dict):
            title = article.get('title', '')
        else:
            title = str(article)
        
        if not title:
            continue
        
        # Polaridad básica
        blob = TextBlob(title)
        polarity = blob.sentiment.polarity
        
        # Peso por recencia adaptativo
        # i=0 (más reciente) -> peso 1.0
        # Disminuye gradualmente según el total de noticias
        recency_weight = max(0.2, 1 - (i * (0.8 / total_news)))
        weighted_polarity = polarity * recency_weight
        sentiments.append(weighted_polarity)
        
        # Detección de keywords
        title_lower = title.lower()
        for kw in CRITICAL_POSITIVE:
            if kw in title_lower:
                critical_kw.append((kw, 'positive'))
        for kw in CRITICAL_NEGATIVE:
            if kw in title_lower:
                critical_kw.append((kw, 'negative'))
    
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    volume = len(news_list)
    
    # Score de volumen (más noticias = más atención)
    # Recalibrado para máximo de 40 noticias
    volume_score = min(1.0, volume / 40)  
    
    if avg_sentiment > 0.1:
        label = "Positivo"
    elif avg_sentiment < -0.1:
        label = "Negativo"
    else:
        label = "Neutral"
    
    return {
        'score': avg_sentiment,
        'label': label,
        'volume': volume,
        'volume_score': volume_score,
        'critical_keywords': critical_kw
    }

def detect_regulatory_factors(news_list):
    """
    Detecta factores políticos/regulatorios en noticias
    
    Returns:
        {
            'has_regulatory_risk': bool,
            'factors_detected': list,
            'sentiment_adjustment': float
        }
    """
    REGULATORY_KEYWORDS = {
        'regulation': -0.5,
        'sec investigation': -1.0,
        'antitrust': -0.8,
        'lawsuit': -0.6,
        'fda approval': 1.0,
        'government contract': 0.8,
        'tariff': -0.5,
        'trade war': -0.7,
        'subsidy': 0.6,
        'sanction': -0.7,
        'compliance': -0.3,
        'policy change': -0.2
    }
    
    if not news_list:
        return {
            'has_regulatory_risk': False,
            'factors_detected': [],
            'sentiment_adjustment': 0.0
        }
    
    factors = []
    adjustment = 0.0
    
    for article in news_list: # Procesar todas para riesgos regulatorios
        # Extraer título
        if isinstance(article, dict):
            title = article.get('title', '')
        else:
            title = str(article)
        
        title_lower = title.lower()
        
        for keyword, weight in REGULATORY_KEYWORDS.items():
            if keyword in title_lower:
                factors.append(keyword)
                adjustment += weight
    
    # Limitar ajuste máximo
    adjustment = max(-1.0, min(1.0, adjustment))
    
    return {
        'has_regulatory_risk': len(factors) > 0,
        'factors_detected': list(set(factors)),
        'sentiment_adjustment': adjustment
    }

def get_sentiment_label(score):
    if score > 0.15:
        return "Positivo"
    elif score < -0.15:
        return "Negativo"
    else:
        return "Neutral"
