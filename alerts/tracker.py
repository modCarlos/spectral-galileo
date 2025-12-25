"""
Alert Performance Tracker

Registra automáticamente cada alerta y trackea su performance en el tiempo.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf


# Paths
TRACKER_FILE = 'data/alerts_tracker.json'
PERFORMANCE_REPORT = 'data/alerts_performance.json'


def load_tracker_data():
    """Carga el historial de alertas trackeadas."""
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {
        'alerts': [],
        'stats': {
            'total_tracked': 0,
            'pending_evaluation': 0,
            'evaluated_7d': 0,
            'evaluated_30d': 0
        }
    }


def save_tracker_data(data):
    """Guarda el historial de alertas."""
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def record_alert_for_tracking(ticker, verdict, confidence, price, details=None):
    """
    Registra una alerta para tracking de performance.
    
    Args:
        ticker: Símbolo del ticker
        verdict: FUERTE COMPRA, COMPRA, VENTA, etc.
        confidence: Porcentaje de confianza (0-100)
        price: Precio al momento de la alerta
        details: Detalles adicionales (dict)
    """
    data = load_tracker_data()
    
    alert_record = {
        'id': len(data['alerts']) + 1,
        'ticker': ticker,
        'verdict': verdict,
        'confidence': confidence,
        'entry_price': price,
        'entry_date': datetime.now().isoformat(),
        'details': details or {},
        
        # Performance tracking
        'price_1d': None,
        'price_7d': None,
        'price_30d': None,
        
        'return_1d': None,
        'return_7d': None,
        'return_30d': None,
        
        'result_7d': None,   # 'WIN', 'LOSS', 'PENDING'
        'result_30d': None,
        
        'last_updated': None,
        'status': 'PENDING'  # PENDING, PARTIAL, COMPLETE
    }
    
    data['alerts'].append(alert_record)
    data['stats']['total_tracked'] += 1
    data['stats']['pending_evaluation'] += 1
    
    save_tracker_data(data)
    
    return alert_record['id']


def update_alert_performance(alert_id=None, ticker=None):
    """
    Actualiza el performance de una alerta específica o todas las pendientes.
    
    Args:
        alert_id: ID específico de alerta a actualizar
        ticker: Ticker específico a actualizar (todas sus alertas)
    """
    data = load_tracker_data()
    now = datetime.now()
    
    updated_count = 0
    
    for alert in data['alerts']:
        # Filtrar por ID o ticker si se especifica
        if alert_id and alert['id'] != alert_id:
            continue
        if ticker and alert['ticker'] != ticker:
            continue
        
        # Skip si ya está completamente evaluado
        if alert['status'] == 'COMPLETE':
            continue
        
        entry_date = datetime.fromisoformat(alert['entry_date'])
        days_since = (now - entry_date).days
        
        # Solo actualizar si han pasado al menos 1 día
        if days_since < 1:
            continue
        
        try:
            # Obtener datos de precios
            stock = yf.Ticker(alert['ticker'])
            hist = stock.history(start=entry_date.date(), end=now.date() + timedelta(days=1))
            
            if hist.empty:
                continue
            
            entry_price = alert['entry_price']
            
            # Actualizar precio 1 día
            if days_since >= 1 and alert['price_1d'] is None:
                if len(hist) >= 2:
                    alert['price_1d'] = float(hist['Close'].iloc[1])
                    alert['return_1d'] = ((alert['price_1d'] - entry_price) / entry_price) * 100
            
            # Actualizar precio 7 días
            if days_since >= 7 and alert['price_7d'] is None:
                target_date = entry_date + timedelta(days=7)
                closest_data = hist[hist.index >= target_date]
                if not closest_data.empty:
                    alert['price_7d'] = float(closest_data['Close'].iloc[0])
                    alert['return_7d'] = ((alert['price_7d'] - entry_price) / entry_price) * 100
                    
                    # Determinar resultado 7d
                    if alert['verdict'] in ['FUERTE COMPRA', 'COMPRA']:
                        alert['result_7d'] = 'WIN' if alert['return_7d'] > 0 else 'LOSS'
                    elif alert['verdict'] == 'VENTA':
                        alert['result_7d'] = 'WIN' if alert['return_7d'] < 0 else 'LOSS'
                    
                    if alert['result_7d'] == 'WIN':
                        data['stats']['evaluated_7d'] += 1
            
            # Actualizar precio 30 días
            if days_since >= 30 and alert['price_30d'] is None:
                target_date = entry_date + timedelta(days=30)
                closest_data = hist[hist.index >= target_date]
                if not closest_data.empty:
                    alert['price_30d'] = float(closest_data['Close'].iloc[0])
                    alert['return_30d'] = ((alert['price_30d'] - entry_price) / entry_price) * 100
                    
                    # Determinar resultado 30d
                    if alert['verdict'] in ['FUERTE COMPRA', 'COMPRA']:
                        alert['result_30d'] = 'WIN' if alert['return_30d'] > 0 else 'LOSS'
                    elif alert['verdict'] == 'VENTA':
                        alert['result_30d'] = 'WIN' if alert['return_30d'] < 0 else 'LOSS'
                    
                    if alert['result_30d'] == 'WIN':
                        data['stats']['evaluated_30d'] += 1
            
            # Actualizar estado
            if alert['price_30d'] is not None:
                alert['status'] = 'COMPLETE'
                data['stats']['pending_evaluation'] -= 1
            elif alert['price_7d'] is not None:
                alert['status'] = 'PARTIAL'
            
            alert['last_updated'] = now.isoformat()
            updated_count += 1
            
        except Exception as e:
            print(f"Error updating alert {alert['id']} ({alert['ticker']}): {e}")
            continue
    
    save_tracker_data(data)
    return updated_count


def calculate_performance_metrics():
    """
    Calcula métricas agregadas de performance.
    """
    data = load_tracker_data()
    alerts = data['alerts']
    
    if not alerts:
        return {
            'error': 'No alerts tracked yet'
        }
    
    # Filtrar alertas evaluadas
    alerts_7d = [a for a in alerts if a['result_7d'] is not None]
    alerts_30d = [a for a in alerts if a['result_30d'] is not None]
    
    metrics = {
        'generated_at': datetime.now().isoformat(),
        'total_alerts': len(alerts),
        'pending_evaluation': data['stats']['pending_evaluation'],
        
        # Performance 7 días
        'performance_7d': {
            'evaluated': len(alerts_7d),
            'wins': len([a for a in alerts_7d if a['result_7d'] == 'WIN']),
            'losses': len([a for a in alerts_7d if a['result_7d'] == 'LOSS']),
            'win_rate': 0,
            'avg_return': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'best_trade': None,
            'worst_trade': None
        },
        
        # Performance 30 días
        'performance_30d': {
            'evaluated': len(alerts_30d),
            'wins': len([a for a in alerts_30d if a['result_30d'] == 'WIN']),
            'losses': len([a for a in alerts_30d if a['result_30d'] == 'LOSS']),
            'win_rate': 0,
            'avg_return': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'best_trade': None,
            'worst_trade': None
        },
        
        # Por veredicto
        'by_verdict': {},
        
        # Por ticker
        'by_ticker': {},
        
        # Por rango de confianza
        'by_confidence': {
            '90-100%': {'count': 0, 'win_rate': 0},
            '80-89%': {'count': 0, 'win_rate': 0},
            '70-79%': {'count': 0, 'win_rate': 0},
            '60-69%': {'count': 0, 'win_rate': 0},
            '<60%': {'count': 0, 'win_rate': 0}
        }
    }
    
    # Calcular métricas 7d
    if alerts_7d:
        returns_7d = [a['return_7d'] for a in alerts_7d]
        wins_7d = [a for a in alerts_7d if a['result_7d'] == 'WIN']
        losses_7d = [a for a in alerts_7d if a['result_7d'] == 'LOSS']
        
        metrics['performance_7d']['win_rate'] = round((len(wins_7d) / len(alerts_7d)) * 100, 2)
        metrics['performance_7d']['avg_return'] = round(sum(returns_7d) / len(returns_7d), 2)
        
        if wins_7d:
            metrics['performance_7d']['avg_win'] = round(sum(a['return_7d'] for a in wins_7d) / len(wins_7d), 2)
            best = max(wins_7d, key=lambda x: x['return_7d'])
            metrics['performance_7d']['best_trade'] = {
                'ticker': best['ticker'],
                'return': round(best['return_7d'], 2),
                'date': best['entry_date']
            }
        
        if losses_7d:
            metrics['performance_7d']['avg_loss'] = round(sum(a['return_7d'] for a in losses_7d) / len(losses_7d), 2)
            worst = min(losses_7d, key=lambda x: x['return_7d'])
            metrics['performance_7d']['worst_trade'] = {
                'ticker': worst['ticker'],
                'return': round(worst['return_7d'], 2),
                'date': worst['entry_date']
            }
    
    # Calcular métricas 30d
    if alerts_30d:
        returns_30d = [a['return_30d'] for a in alerts_30d]
        wins_30d = [a for a in alerts_30d if a['result_30d'] == 'WIN']
        losses_30d = [a for a in alerts_30d if a['result_30d'] == 'LOSS']
        
        metrics['performance_30d']['win_rate'] = round((len(wins_30d) / len(alerts_30d)) * 100, 2)
        metrics['performance_30d']['avg_return'] = round(sum(returns_30d) / len(returns_30d), 2)
        
        if wins_30d:
            metrics['performance_30d']['avg_win'] = round(sum(a['return_30d'] for a in wins_30d) / len(wins_30d), 2)
            best = max(wins_30d, key=lambda x: x['return_30d'])
            metrics['performance_30d']['best_trade'] = {
                'ticker': best['ticker'],
                'return': round(best['return_30d'], 2),
                'date': best['entry_date']
            }
        
        if losses_30d:
            metrics['performance_30d']['avg_loss'] = round(sum(a['return_30d'] for a in losses_30d) / len(losses_30d), 2)
            worst = min(losses_30d, key=lambda x: x['return_30d'])
            metrics['performance_30d']['worst_trade'] = {
                'ticker': worst['ticker'],
                'return': round(worst['return_30d'], 2),
                'date': worst['entry_date']
            }
    
    # Agrupar por veredicto
    verdicts = set(a['verdict'] for a in alerts)
    for verdict in verdicts:
        verdict_alerts = [a for a in alerts_7d if a['verdict'] == verdict]
        if verdict_alerts:
            wins = len([a for a in verdict_alerts if a['result_7d'] == 'WIN'])
            metrics['by_verdict'][verdict] = {
                'count': len(verdict_alerts),
                'win_rate': round((wins / len(verdict_alerts)) * 100, 2)
            }
    
    # Agrupar por ticker
    tickers = set(a['ticker'] for a in alerts)
    for ticker in tickers:
        ticker_alerts = [a for a in alerts_7d if a['ticker'] == ticker]
        if ticker_alerts:
            wins = len([a for a in ticker_alerts if a['result_7d'] == 'WIN'])
            returns = [a['return_7d'] for a in ticker_alerts]
            metrics['by_ticker'][ticker] = {
                'count': len(ticker_alerts),
                'win_rate': round((wins / len(ticker_alerts)) * 100, 2),
                'avg_return': round(sum(returns) / len(returns), 2)
            }
    
    # Agrupar por confianza
    for alert in alerts_7d:
        conf = alert['confidence']
        if conf >= 90:
            bucket = '90-100%'
        elif conf >= 80:
            bucket = '80-89%'
        elif conf >= 70:
            bucket = '70-79%'
        elif conf >= 60:
            bucket = '60-69%'
        else:
            bucket = '<60%'
        
        metrics['by_confidence'][bucket]['count'] += 1
        if alert['result_7d'] == 'WIN':
            metrics['by_confidence'][bucket]['win_rate'] += 1
    
    # Calcular win rate por bucket de confianza
    for bucket in metrics['by_confidence']:
        if metrics['by_confidence'][bucket]['count'] > 0:
            wr = (metrics['by_confidence'][bucket]['win_rate'] / metrics['by_confidence'][bucket]['count']) * 100
            metrics['by_confidence'][bucket]['win_rate'] = round(wr, 2)
    
    # Guardar reporte
    os.makedirs(os.path.dirname(PERFORMANCE_REPORT), exist_ok=True)
    with open(PERFORMANCE_REPORT, 'w') as f:
        json.dump(metrics, f, indent=2, default=str)
    
    return metrics


def get_pending_alerts():
    """Retorna alertas pendientes de evaluación completa."""
    data = load_tracker_data()
    return [a for a in data['alerts'] if a['status'] != 'COMPLETE']


def get_recent_alerts(days=7):
    """Retorna alertas de los últimos N días."""
    data = load_tracker_data()
    cutoff = datetime.now() - timedelta(days=days)
    
    return [
        a for a in data['alerts']
        if datetime.fromisoformat(a['entry_date']) >= cutoff
    ]


def get_alert_by_id(alert_id):
    """Obtiene una alerta específica por ID."""
    data = load_tracker_data()
    for alert in data['alerts']:
        if alert['id'] == alert_id:
            return alert
    return None


if __name__ == '__main__':
    # Test básico
    print("Testing Alert Tracker...")
    
    # Ejemplo de uso
    alert_id = record_alert_for_tracking(
        ticker='AAPL',
        verdict='FUERTE COMPRA',
        confidence=75,
        price=185.20,
        details={'rsi': 28.5, 'macd': 'Bullish'}
    )
    
    print(f"✅ Alert recorded: ID {alert_id}")
    
    # Actualizar performance
    updated = update_alert_performance()
    print(f"✅ Updated {updated} alerts")
    
    # Calcular métricas
    metrics = calculate_performance_metrics()
    print(f"✅ Metrics calculated: {metrics['total_alerts']} total alerts")
