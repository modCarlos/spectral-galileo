# 🤖 FASE 2: Machine Learning Básico - Plan Detallado

**Rama:** `feature/phase2-ml-basic`  
**Duración:** 6-12 meses (65-90 horas)  
**Fecha inicio:** 26 de Diciembre, 2025  
**Meta:** Mejorar de 18-25% a 22-32% annual return (Sharpe 1.5→2.0)

---

## 📊 Estado Inicial (Post-Fase 1)

**Performance actual:**
```
Annual Return:  18-25% (con high conviction)
Win Rate:       73-80%
Sharpe Ratio:   1.2-1.6
Max Drawdown:   12-18%
```

**Infraestructura existente:**
- ✅ 68 tickers con datos históricos (2015-2024)
- ✅ 13 high conviction tickers validados
- ✅ Sistema de scoring rule-based optimizado
- ✅ Backtesting framework funcional
- ✅ Risk management con ATR

---

## 🎯 Objetivos de Fase 2

### Meta Principal
Agregar **predicción ML** que complemente (no reemplace) el sistema rule-based actual.

### Enfoque: Ensemble Hybrid
```
Final Score = 50% Rule-Based + 50% ML Prediction
```

**Por qué hybrid?**
- Rule-based: Interpretable, confiable, probado
- ML: Captura patrones no-lineales, aprende de datos
- Ensemble: Reduce overfitting, mayor robustez

### Mejoras Esperadas
```
Win Rate:      73-80% → 78-85% (+5-8%)
Annual Return: 18-25% → 22-32% (+4-7%)
Sharpe Ratio:  1.2-1.6 → 1.5-2.0 (+0.3-0.4)
```

---

## 📚 Índice de Tareas

**Tarea 2.1:** Scikit-learn Models (40-60 horas)  
**Tarea 2.2:** Feature Store Simple (15-20 horas)  
**Tarea 2.3:** Ensemble Híbrido (10 horas)

**Total:** 65-90 horas (~4-5 horas/semana durante 3-4 meses)

---

## 🔬 TAREA 2.1: Scikit-learn Models

**Prioridad:** 🔥🔥🔥 MÁXIMA  
**Tiempo estimado:** 40-60 horas  
**Impacto esperado:** +8-12% win rate

### Objetivo

Implementar 3 modelos ML básicos que predigan BUY/HOLD/SELL basados en features técnicos.

### Modelos a Implementar

#### Modelo 1: Random Forest (Baseline)

**Por qué Random Forest?**
- ✅ Fácil de entrenar
- ✅ Robusto a outliers
- ✅ Feature importance built-in
- ✅ Poco overfitting
- ✅ No requiere feature scaling

**Features a usar (15-20):**
```python
Technical (10):
- RSI (14, 7, 21)
- MACD (line, signal, histogram)
- Bollinger Bands (upper, lower, %B)
- ADX
- Stochastic K/D

Volume (3):
- Volume ratio (vs 20-day avg)
- OBV slope
- Volume trend

Momentum (3):
- Price momentum (10, 20, 50 day)
- Rate of Change

Volatility (2):
- ATR normalized
- Historical volatility

Derived (2):
- Distance from SMA 50/200
- Trend strength
```

**Target variable:**
```python
# Label generation (look-ahead 5-10 days)
if future_return > +5%:
    label = 'BUY'
elif future_return < -3%:
    label = 'SELL'
else:
    label = 'HOLD'
```

**Implementación:**

```python
# ml_models/random_forest_model.py

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
import numpy as np

class TradingRandomForest:
    """
    Random Forest classifier for trading signals
    """
    
    def __init__(self, n_estimators=100, max_depth=10):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=50,
            min_samples_leaf=20,
            random_state=42,
            n_jobs=-1
        )
        self.feature_names = None
        self.feature_importance = None
    
    def prepare_features(self, df):
        """Extract features from raw OHLCV data"""
        
        features = pd.DataFrame(index=df.index)
        
        # Technical indicators (RSI, MACD, etc)
        features['rsi_14'] = df['RSI']
        features['macd'] = df['MACD']
        features['macd_signal'] = df['MACD_Signal']
        features['bb_pct'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        features['adx'] = df['ADX']
        features['stoch_k'] = df['Stoch_K']
        
        # Volume
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Momentum
        features['momentum_10'] = df['Close'].pct_change(10)
        features['momentum_20'] = df['Close'].pct_change(20)
        
        # Price distance from MAs
        features['dist_sma50'] = (df['Close'] - df['SMA_50']) / df['SMA_50']
        features['dist_sma200'] = (df['Close'] - df['SMA_200']) / df['SMA_200']
        
        # Volatility
        features['atr_norm'] = df['ATR'] / df['Close']
        
        return features.dropna()
    
    def generate_labels(self, df, forward_window=10, buy_threshold=0.05, sell_threshold=-0.03):
        """
        Generate labels based on future returns
        
        Args:
            df: DataFrame with price data
            forward_window: Days to look ahead
            buy_threshold: Min return for BUY label (5%)
            sell_threshold: Max return for SELL label (-3%)
        """
        
        # Calculate forward returns
        future_returns = df['Close'].pct_change(forward_window).shift(-forward_window)
        
        # Generate labels
        labels = pd.Series('HOLD', index=df.index)
        labels[future_returns > buy_threshold] = 'BUY'
        labels[future_returns < sell_threshold] = 'SELL'
        
        return labels
    
    def train(self, X_train, y_train):
        """Train the model"""
        
        self.feature_names = X_train.columns.tolist()
        
        print(f"Training Random Forest...")
        print(f"  Features: {len(self.feature_names)}")
        print(f"  Samples: {len(X_train)}")
        print(f"  Class distribution: {y_train.value_counts().to_dict()}")
        
        self.model.fit(X_train, y_train)
        
        # Store feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"✅ Training complete!")
        print(f"\nTop 5 features:")
        print(self.feature_importance.head())
    
    def predict(self, X):
        """Predict labels"""
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Predict probabilities for each class"""
        return self.model.predict_proba(X)
    
    def get_signal_with_confidence(self, X):
        """
        Get signal with confidence score
        
        Returns:
            dict: {'signal': 'BUY'/'HOLD'/'SELL', 'confidence': 0.0-1.0}
        """
        
        prediction = self.predict(X)[0]
        probabilities = self.predict_proba(X)[0]
        
        # Confidence = max probability
        confidence = probabilities.max()
        
        return {
            'signal': prediction,
            'confidence': confidence,
            'probabilities': {
                label: prob 
                for label, prob in zip(self.model.classes_, probabilities)
            }
        }
```

**Script de entrenamiento:**

```python
# ml_models/train_rf.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from random_forest_model import TradingRandomForest
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import pickle

def load_and_prepare_data(ticker, data_dir='backtesting/data'):
    """Load ticker data and prepare for ML"""
    
    # Load raw data
    df = pd.read_csv(f"{data_dir}/{ticker}.csv", parse_dates=['Date'], index_col='Date')
    
    # Calculate indicators (use existing indicators.py)
    from indicators import TechnicalIndicators
    indicators = TechnicalIndicators()
    
    # Add all indicators
    df = indicators.calculate_all(df)
    
    return df

def train_model_for_ticker(ticker):
    """Train Random Forest model for a specific ticker"""
    
    print(f"\n{'='*70}")
    print(f"Training ML Model: {ticker}")
    print(f"{'='*70}\n")
    
    # Load data
    df = load_and_prepare_data(ticker)
    
    # Initialize model
    rf_model = TradingRandomForest(n_estimators=200, max_depth=15)
    
    # Prepare features and labels
    X = rf_model.prepare_features(df)
    y = rf_model.generate_labels(df)
    
    # Align X and y
    common_idx = X.index.intersection(y.index)
    X = X.loc[common_idx]
    y = y.loc[common_idx]
    
    # Time series split (respecting temporal order)
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Use last split for training (most recent data)
    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    # Train
    rf_model.train(X_train, y_train)
    
    # Evaluate on test set
    print(f"\n{'='*70}")
    print("EVALUATION ON TEST SET (Out-of-sample)")
    print(f"{'='*70}\n")
    
    y_pred = rf_model.predict(X_test)
    
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model
    os.makedirs('ml_models/saved_models', exist_ok=True)
    model_path = f'ml_models/saved_models/rf_{ticker}.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)
    
    print(f"\n✅ Model saved: {model_path}")
    
    return rf_model

def train_all_high_conviction():
    """Train models for all high conviction tickers"""
    
    import json
    
    with open('watchlist_high_conviction.json') as f:
        tickers = json.load(f)
    
    print(f"Training models for {len(tickers)} high conviction tickers...")
    
    results = {}
    
    for ticker in tickers:
        try:
            model = train_model_for_ticker(ticker)
            results[ticker] = 'success'
        except Exception as e:
            print(f"❌ Error training {ticker}: {e}")
            results[ticker] = 'failed'
    
    # Summary
    print(f"\n{'='*70}")
    print("TRAINING SUMMARY")
    print(f"{'='*70}")
    
    success = sum(1 for v in results.values() if v == 'success')
    print(f"✅ Success: {success}/{len(tickers)}")
    print(f"❌ Failed: {len(tickers) - success}/{len(tickers)}")
    
    if success < len(tickers):
        failed = [k for k, v in results.items() if v == 'failed']
        print(f"\nFailed tickers: {', '.join(failed)}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', type=str, help='Train single ticker')
    parser.add_argument('--all', action='store_true', help='Train all high conviction')
    
    args = parser.parse_args()
    
    if args.all:
        train_all_high_conviction()
    elif args.ticker:
        train_model_for_ticker(args.ticker)
    else:
        print("Usage: python train_rf.py --ticker NVDA  OR  --all")
```

**Tiempo:** 20-30 horas

---

#### Modelo 2: XGBoost (Performance)

**Por qué XGBoost?**
- ✅ Mejor performance que Random Forest
- ✅ Maneja datos desbalanceados bien
- ✅ Regularización built-in
- ✅ Rápido en predicción

**Implementación:**

```python
# ml_models/xgboost_model.py

import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

class TradingXGBoost:
    """XGBoost classifier for trading signals"""
    
    def __init__(self, n_estimators=200, max_depth=8, learning_rate=0.1):
        self.label_encoder = LabelEncoder()
        
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softprob',
            random_state=42,
            n_jobs=-1
        )
    
    def train(self, X_train, y_train):
        """Train XGBoost model"""
        
        # Encode labels to integers
        y_encoded = self.label_encoder.fit_transform(y_train)
        
        print(f"Training XGBoost...")
        print(f"  Features: {X_train.shape[1]}")
        print(f"  Samples: {len(X_train)}")
        
        self.model.fit(
            X_train, 
            y_encoded,
            eval_set=[(X_train, y_encoded)],
            verbose=False
        )
        
        print(f"✅ Training complete!")
    
    def predict(self, X):
        """Predict labels"""
        y_pred = self.model.predict(X)
        return self.label_encoder.inverse_transform(y_pred)
    
    def predict_proba(self, X):
        """Predict probabilities"""
        return self.model.predict_proba(X)
```

**Tiempo:** 10-15 horas

---

#### Modelo 3: Logistic Regression (Interpretable)

**Por qué Logistic Regression?**
- ✅ Muy interpretable (coeficientes = feature importance)
- ✅ Rápido de entrenar
- ✅ Baseline simple
- ✅ Buen para entender relaciones lineales

**Implementación:**

```python
# ml_models/logistic_model.py

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class TradingLogistic:
    """Logistic Regression for trading signals"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = LogisticRegression(
            multi_class='multinomial',
            solver='lbfgs',
            max_iter=1000,
            random_state=42
        )
    
    def train(self, X_train, y_train):
        """Train model with feature scaling"""
        
        # Scale features (important for LogReg)
        X_scaled = self.scaler.fit_transform(X_train)
        
        print(f"Training Logistic Regression...")
        self.model.fit(X_scaled, y_train)
        print(f"✅ Training complete!")
    
    def predict(self, X):
        """Predict with scaling"""
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
```

**Tiempo:** 5-10 horas

---

### Resultado Esperado Tarea 2.1

**Entregables:**
1. ✅ 3 modelos ML implementados (RF, XGBoost, LogReg)
2. ✅ Scripts de entrenamiento para cada ticker
3. ✅ Modelos entrenados guardados en `ml_models/saved_models/`
4. ✅ Evaluación de performance (classification report)
5. ✅ Feature importance analysis

**Métricas esperadas (test set):**
```
Accuracy:        65-75%
Precision (BUY): 70-80%
Recall (BUY):    60-70%
F1-Score:        65-75%
```

---

## 💾 TAREA 2.2: Feature Store Simple

**Prioridad:** 🔥🔥 ALTA  
**Tiempo estimado:** 15-20 horas  
**Impacto:** Eficiencia (+300% velocidad de entrenamiento)

### Objetivo

Crear sistema para almacenar features pre-calculados y evitar re-calcular indicadores cada vez.

### Implementación SQLite

**Por qué SQLite?**
- ✅ Built-in Python (sin instalación)
- ✅ Rápido para lecturas
- ✅ Fácil de versionar (archivo único)
- ✅ Sin servidor necesario

**Estructura:**

```python
# ml_models/feature_store.py

import sqlite3
import pandas as pd
from pathlib import Path

class FeatureStore:
    """
    Simple feature store using SQLite
    """
    
    def __init__(self, db_path='data/features.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        """Create feature tables"""
        
        cursor = self.conn.cursor()
        
        # Main features table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date DATE NOT NULL,
                
                -- Price data
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                
                -- Technical indicators
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                bb_upper REAL,
                bb_lower REAL,
                adx REAL,
                stoch_k REAL,
                atr REAL,
                
                -- Derived features
                momentum_10 REAL,
                momentum_20 REAL,
                volume_ratio REAL,
                dist_sma50 REAL,
                dist_sma200 REAL,
                
                -- Target (for training)
                future_return_5d REAL,
                future_return_10d REAL,
                label TEXT,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(ticker, date)
            )
        """)
        
        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ticker_date 
            ON features(ticker, date)
        """)
        
        self.conn.commit()
    
    def store_features(self, ticker, df):
        """
        Store features for a ticker
        
        Args:
            ticker: Ticker symbol
            df: DataFrame with features
        """
        
        # Prepare data
        df_copy = df.copy()
        df_copy['ticker'] = ticker
        df_copy['date'] = df_copy.index
        
        # Insert/replace
        df_copy.to_sql(
            'features',
            self.conn,
            if_exists='append',
            index=False
        )
        
        self.conn.commit()
        
        print(f"✅ Stored {len(df_copy)} rows for {ticker}")
    
    def get_features(self, ticker, start_date=None, end_date=None):
        """
        Retrieve features for a ticker
        
        Args:
            ticker: Ticker symbol
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DataFrame with features
        """
        
        query = "SELECT * FROM features WHERE ticker = ?"
        params = [ticker]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        return df
    
    def list_tickers(self):
        """Get list of tickers in feature store"""
        
        query = "SELECT DISTINCT ticker FROM features"
        return pd.read_sql_query(query, self.conn)['ticker'].tolist()
    
    def get_latest_date(self, ticker):
        """Get latest date for a ticker"""
        
        query = "SELECT MAX(date) as latest FROM features WHERE ticker = ?"
        result = pd.read_sql_query(query, self.conn, params=[ticker])
        return result['latest'].iloc[0]
```

**Script de población:**

```python
# ml_models/populate_feature_store.py

from feature_store import FeatureStore
from random_forest_model import TradingRandomForest
import json

def populate_all_high_conviction():
    """Calculate and store features for all high conviction tickers"""
    
    print("Populating feature store...")
    
    fs = FeatureStore()
    rf_model = TradingRandomForest()
    
    with open('watchlist_high_conviction.json') as f:
        tickers = json.load(f)
    
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        
        try:
            # Load data
            df = pd.read_csv(f'backtesting/data/{ticker}.csv', 
                           parse_dates=['Date'], index_col='Date')
            
            # Calculate indicators
            from indicators import TechnicalIndicators
            indicators = TechnicalIndicators()
            df = indicators.calculate_all(df)
            
            # Generate features
            features = rf_model.prepare_features(df)
            
            # Generate labels
            features['label'] = rf_model.generate_labels(df)
            
            # Calculate future returns
            features['future_return_5d'] = df['Close'].pct_change(5).shift(-5)
            features['future_return_10d'] = df['Close'].pct_change(10).shift(-10)
            
            # Store
            fs.store_features(ticker, features)
            
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
    
    print(f"\n✅ Feature store populated!")
    print(f"   Tickers: {len(fs.list_tickers())}")

if __name__ == '__main__':
    populate_all_high_conviction()
```

**Tiempo:** 15-20 horas

---

## 🔗 TAREA 2.3: Ensemble Híbrido

**Prioridad:** 🔥🔥🔥 CRÍTICA  
**Tiempo estimado:** 10 horas  
**Impacto:** +5-8% win rate (sinergia de ambos sistemas)

### Objetivo

Combinar scoring rule-based existente con predicciones ML en un ensemble híbrido.

### Estrategia de Combinación

**Enfoque:** Weighted Average

```python
Final_Score = (
    rule_based_score * weight_rules +
    ml_probability * weight_ml
)

# Weights ajustables:
weight_rules = 0.50  # 50%
weight_ml = 0.50     # 50%
```

### Implementación

**Modificar agent.py:**

```python
# agent.py - agregar método

def run_analysis_with_ml(self, pre_data=None):
    """
    Enhanced analysis with ML predictions
    Combines rule-based scoring with ML model
    """
    
    # 1. Run traditional rule-based analysis
    traditional_results = self.run_analysis(pre_data=pre_data)
    
    # 2. Load ML model (if available)
    ml_model_path = f'ml_models/saved_models/rf_{self.ticker}.pkl'
    
    if not os.path.exists(ml_model_path):
        print(f"⚠️  No ML model for {self.ticker}, using rule-based only")
        return traditional_results
    
    # Load model
    import pickle
    with open(ml_model_path, 'rb') as f:
        ml_model = pickle.load(f)
    
    # 3. Prepare features for ML
    ticker_data = pre_data.get('ticker_data', {})
    df = pd.DataFrame(ticker_data)
    
    features = ml_model.prepare_features(df)
    
    # Get latest features (current state)
    latest_features = features.iloc[[-1]]
    
    # 4. Get ML prediction
    ml_prediction = ml_model.get_signal_with_confidence(latest_features)
    
    # 5. Combine scores
    rule_based_score = traditional_results['strategy']['confidence'] / 100.0
    ml_score = ml_prediction['confidence']
    
    # Weighted ensemble
    ensemble_score = (
        rule_based_score * 0.50 +
        ml_score * 0.50
    )
    
    # 6. Determine final verdict
    if ensemble_score > 0.70:
        final_verdict = "FUERTE COMPRA 🚀"
    elif ensemble_score > 0.50:
        final_verdict = "COMPRA 🟢"
    elif ensemble_score < 0.30:
        final_verdict = "VENTA 🔴"
    else:
        final_verdict = "NEUTRAL ⚪"
    
    # 7. Enhance results with ML info
    traditional_results['ml_prediction'] = ml_prediction
    traditional_results['ensemble_score'] = ensemble_score
    traditional_results['strategy']['verdict'] = final_verdict
    traditional_results['strategy']['confidence'] = ensemble_score * 100
    traditional_results['strategy']['breakdown'] = {
        'rule_based': rule_based_score,
        'ml_model': ml_score,
        'ensemble': ensemble_score
    }
    
    return traditional_results
```

**Actualizar main.py:**

```python
# main.py - agregar flag --ml

parser.add_argument('--ml', action='store_true',
                    help='Usar ensemble híbrido (rule-based + ML)')

# En análisis de ticker:
if args.ml:
    results = agent.run_analysis_with_ml(pre_data=data)
else:
    results = agent.run_analysis(pre_data=data)
```

**Tiempo:** 10 horas

---

## 📊 Fase 2 Completa - Resultados Esperados

### Performance Proyectada

| Métrica | Post-Fase 1 | Post-Fase 2 | Mejora |
|---------|-------------|-------------|--------|
| Annual Return | 18-25% | **22-32%** | +4-7% 🚀 |
| Sharpe Ratio | 1.2-1.6 | **1.5-2.0** | +0.3-0.4 📈 |
| Win Rate | 73-80% | **78-85%** | +5-8% ✅ |
| Precision | N/A | **75-85%** | NEW 🎯 |
| False Positives | 20-27% | **15-22%** | -5% 🛡️ |

### Tiempo Total Invertido

```
Tarea 2.1: ML Models            →  45 horas
Tarea 2.2: Feature Store        →  18 horas
Tarea 2.3: Ensemble Hybrid      →  10 horas
Testing & Validation            →  17 horas
---------------------------------------------------
TOTAL                           →  90 horas
```

**Ritmo:** 4 horas/semana = **22 semanas (5 meses)**  
**Acelerado:** 8 horas/semana = **11 semanas (2.5 meses)**

---

## 📅 Plan de Ejecución Propuesto

### Mes 1 (Enero 2026): Random Forest

**Semana 1-2:**
- Implementar `random_forest_model.py`
- Feature engineering básico
- Script de entrenamiento

**Semana 3-4:**
- Entrenar en 3-5 tickers (test)
- Evaluar performance
- Ajustar hiperparámetros

**Entregable:** Random Forest funcionando en high conviction tickers

---

### Mes 2 (Febrero 2026): XGBoost + Feature Store

**Semana 1:**
- Implementar `xgboost_model.py`
- Comparar con Random Forest

**Semana 2-3:**
- Implementar Feature Store
- Poblar con datos históricos

**Semana 4:**
- Scripts de actualización
- Optimización de queries

**Entregable:** XGBoost + Feature Store operacional

---

### Mes 3 (Marzo 2026): Ensemble Hybrid

**Semana 1-2:**
- Implementar ensemble en agent.py
- Actualizar CLI con flag --ml

**Semana 3:**
- Testing exhaustivo
- Comparación rule-based vs ensemble

**Semana 4:**
- Ajuste de pesos (50/50 vs 60/40 vs 70/30)
- Backtest validation

**Entregable:** Sistema híbrido completo y validado

---

## ✅ Checklist de Progreso

### Setup Inicial
- [ ] Rama `feature/phase2-ml-basic` creada
- [ ] Instalar dependencias: `pip install scikit-learn xgboost`
- [ ] Crear carpeta `ml_models/`

### Tarea 2.1: ML Models
- [ ] `random_forest_model.py` implementado
- [ ] `xgboost_model.py` implementado
- [ ] `logistic_model.py` implementado
- [ ] Script `train_rf.py` funcional
- [ ] Modelos entrenados para high conviction
- [ ] Feature importance analizado
- [ ] Performance > 70% accuracy

### Tarea 2.2: Feature Store
- [ ] `feature_store.py` implementado
- [ ] Database schema creado
- [ ] Script `populate_feature_store.py` funcional
- [ ] Datos históricos almacenados
- [ ] Queries optimizadas

### Tarea 2.3: Ensemble
- [ ] `run_analysis_with_ml()` en agent.py
- [ ] Flag `--ml` en main.py
- [ ] Weighted ensemble funcionando
- [ ] Backtesting validation
- [ ] Comparación before/after

### Finalización
- [ ] Performance targets alcanzados
- [ ] Documentation completa
- [ ] Git commit final
- [ ] Merge a main

---

## 🎯 Criterios de Éxito

### Must-Have (Obligatorio)
- ✅ ML accuracy > 65% (test set)
- ✅ Ensemble win rate > 78%
- ✅ Annual return > 22%
- ✅ No degradación de Sharpe ratio

### Nice-to-Have (Deseable)
- ✅ ML accuracy > 70%
- ✅ Win rate > 80%
- ✅ Annual return > 28%
- ✅ Sharpe ratio > 1.8

### Red Flags (Revisar si pasa)
- ❌ ML accuracy < 60% → Overfitting o features incorrectos
- ❌ Ensemble peor que rule-based → Pesos incorrectos
- ❌ Training time > 10 min/ticker → Optimizar features

---

## 🚀 Próximos Pasos INMEDIATOS

**Hoy (26 Dic 2025):**
```bash
# 1. Instalar dependencias ML
pip install scikit-learn xgboost

# 2. Crear estructura
mkdir -p ml_models/saved_models

# 3. Copiar template de random_forest_model.py
# (Se creará en próximo paso)
```

**Esta Semana:**
- Implementar Random Forest básico
- Entrenar en NVDA (top performer)
- Evaluar resultados iniciales

**Próximas 2 Semanas:**
- Entrenar en todos los high conviction
- Feature engineering refinement
- Comparar con rule-based

---

## 💡 Tips Importantes

### 1. Avoid Overfitting ⚠️

**Estrategias:**
- ✅ Time series split (NO random split)
- ✅ Out-of-sample testing SIEMPRE
- ✅ Regularización (max_depth, min_samples)
- ✅ Cross-validation temporal

### 2. Feature Engineering > Model Selection

**Focus en:**
- Indicadores con lag (no future info)
- Features derivados (ratios, cambios)
- Normalización cuando sea necesario
- Menos features > muchos features ruidosos

### 3. Start Simple, Add Complexity

**Orden:**
1. Random Forest básico (10 features)
2. Evaluar → Funciona?
3. Agregar features gradualmente
4. Re-evaluar después de cada adición

### 4. Benchmark Constantly

**Comparar siempre:**
- ML vs Rule-based
- ML vs Buy & Hold
- ML vs S&P 500
- ML Actual vs ML Histórico (drift detection)

---

## 📚 Referencias

**Libros:**
- "Hands-On Machine Learning" - Géron (Capítulos 3, 6, 7)
- "Python for Finance" - Yves Hilpisch

**Papers:**
- "Random Forests" - Breiman (2001)
- "XGBoost: A Scalable Tree Boosting System" - Chen & Guestrin (2016)

**Recursos Online:**
- Scikit-learn docs: https://scikit-learn.org
- XGBoost docs: https://xgboost.readthedocs.io

---

**Última actualización:** 26 de Diciembre, 2025  
**Próxima revisión:** Marzo 2026 (mid-Fase 2)

¡Empecemos! 🤖
