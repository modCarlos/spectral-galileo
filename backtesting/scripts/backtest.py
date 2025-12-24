"""
Backtesting simple usando indicadores técnicos
Evita look-ahead bias usando solo datos históricos disponibles
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import market_data
import indicators
from colorama import Fore, Style

def simple_backtest(ticker, start_date=None, end_date=None, initial_capital=10000):
    """
    Backtesting usando SOLO indicadores técnicos
    
    Reglas de Trading (MÁS AGRESIVAS que el agente principal):
    - COMPRA: RSI < 45 Y precio > SMA200 (antes RSI < 35)
    - VENTA: RSI > 65 O pérdida > 10% O ganancia > 15% (antes RSI > 70, -15%, +25%)
    - HOLD: Cualquier otro caso
    
    NOTA: Estas reglas son más agresivas que el agente de análisis principal
          para generar más actividad en el backtesting y evaluar la estrategia.
    
    Args:
        ticker: Símbolo de la acción
        start_date: Fecha inicial (default: hace 1 año)
        end_date: Fecha final (default: hoy)
        initial_capital: Capital inicial
    
    Returns:
        dict con resultados del backtest
    """
    # Defaults: último año
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"BACKTESTING: {ticker}")
    print(f"Período: {start_date} a {end_date}")
    print(f"Capital Inicial: ${initial_capital:,.2f}")
    print(f"Estrategia: Indicadores Técnicos (RSI + SMA) - Reglas Agresivas")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Descargar datos históricos
    print("Descargando datos históricos...")
    t = market_data.get_ticker_data(ticker)
    df = t.history(start=start_date, end=end_date)
    
    if df.empty:
        print(f"{Fore.RED}No se pudieron obtener datos históricos{Style.RESET_ALL}")
        return {"error": "No data"}
    
    # Calcular indicadores
    print("Calculando indicadores técnicos...")
    df = indicators.add_all_indicators(df)
    
    # Variables de trading
    cash = initial_capital
    shares = 0
    buy_price = 0
    trades = []
    
    # Iterar por cada día (empezar después de SMA200)
    for i in range(200, len(df)):
        date = df.index[i]
        price = df['Close'].iloc[i]
        rsi = df['RSI'].iloc[i]
        sma_200 = df['SMA_200'].iloc[i]
        
        # Skip si hay NaN
        if pd.isna(rsi) or pd.isna(sma_200):
            continue
        
        # Señal de COMPRA (reglas agresivas)
        if shares == 0 and cash > price:
            if rsi < 45 and price > sma_200:  # RSI < 45 (antes era < 35)
                shares_to_buy = int(cash * 0.95 / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    shares += shares_to_buy
                    cash -= cost
                    buy_price = price
                    
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'cost': cost,
                        'rsi': rsi,
                        'reason': f'RSI Oversold ({rsi:.1f})'
                    })
        
        # Señal de VENTA (reglas agresivas)
        elif shares > 0:
            pnl_pct = ((price - buy_price) / buy_price) * 100
            
            should_sell = False
            reason = ""
            
            if rsi > 65:  # RSI > 65 (antes era > 70)
                should_sell = True
                reason = f"RSI Overbought ({rsi:.1f})"
            elif pnl_pct < -10:  # Stop loss -10% (antes era -15%)
                should_sell = True
                reason = f"Stop Loss ({pnl_pct:.1f}%)"
            elif pnl_pct > 15:  # Take profit +15% (antes era +25%)
                should_sell = True
                reason = f"Take Profit ({pnl_pct:.1f}%)"
            
            if should_sell:
                proceeds = shares * price
                cash += proceeds
                
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': price,
                    'shares': shares,
                    'proceeds': proceeds,
                    'pnl': proceeds - (shares * buy_price),
                    'pnl_pct': pnl_pct,
                    'rsi': rsi,
                    'reason': reason
                })
                
                shares = 0
                buy_price = 0
    
    # Cerrar posición final si existe
    final_price = df['Close'].iloc[-1]
    if shares > 0:
        proceeds = shares * final_price
        pnl_pct = ((final_price - buy_price) / buy_price) * 100
        
        trades.append({
            'date': df.index[-1],
            'action': 'SELL',
            'price': final_price,
            'shares': shares,
            'proceeds': proceeds,
            'pnl': proceeds - (shares * buy_price),
            'pnl_pct': pnl_pct,
            'rsi': df['RSI'].iloc[-1],
            'reason': 'Cierre final'
        })
        
        cash += proceeds
        shares = 0
    
    # Calcular resultados
    final_value = cash + (shares * final_price)
    total_return = final_value - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    # Buy & Hold comparison
    initial_price = df['Close'].iloc[200]
    buy_hold_shares = initial_capital / initial_price
    buy_hold_value = buy_hold_shares * final_price
    buy_hold_return = buy_hold_value - initial_capital
    buy_hold_pct = (buy_hold_return / initial_capital) * 100
    
    # Estadísticas de trades
    sell_trades = [t for t in trades if t['action'] == 'SELL' and 'pnl' in t]
    winning_trades = [t for t in sell_trades if t['pnl'] > 0]
    losing_trades = [t for t in sell_trades if t['pnl'] < 0]
    
    # Imprimir resultados
    print(f"\n{Fore.CYAN}{'='*80}")
    print("RESULTADOS DEL BACKTESTING")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"📊 PERFORMANCE")
    print(f"Capital Inicial:     ${initial_capital:,.2f}")
    print(f"Capital Final:       ${final_value:,.2f}")
    
    if total_return > 0:
        print(f"Ganancia/Pérdida:    {Fore.GREEN}+${total_return:,.2f} (+{return_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Ganancia/Pérdida:    {Fore.RED}${total_return:,.2f} ({return_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n💼 POSICIÓN FINAL")
    print(f"Acciones:            {shares}")
    print(f"Cash:                ${cash:,.2f}")
    
    print(f"\n{Fore.YELLOW}📈 COMPARACIÓN: Buy & Hold{Style.RESET_ALL}")
    print(f"Valor Buy & Hold:    ${buy_hold_value:,.2f}")
    
    if buy_hold_return > 0:
        print(f"Retorno Buy & Hold:  {Fore.GREEN}+${buy_hold_return:,.2f} (+{buy_hold_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Retorno Buy & Hold:  {Fore.RED}${buy_hold_return:,.2f} ({buy_hold_pct:.2f}%){Style.RESET_ALL}")
    
    if return_pct > buy_hold_pct:
        diff = return_pct - buy_hold_pct
        print(f"\n{Fore.GREEN}✅ La estrategia SUPERÓ a Buy & Hold por {diff:.2f}%{Style.RESET_ALL}")
    else:
        diff = buy_hold_pct - return_pct
        print(f"\n{Fore.RED}❌ Buy & Hold fue mejor por {diff:.2f}%{Style.RESET_ALL}")
    
    # Reglas de la estrategia
    print(f"\n📋 REGLAS DE LA ESTRATEGIA (AGRESIVAS)")
    print(f"Compra:  RSI < 45 Y Precio > SMA200")
    print(f"Venta:   RSI > 65 O Pérdida > 10% O Ganancia > 15%")
    
    # Estadísticas de trades
    print(f"\n📊 ESTADÍSTICAS DE TRADING")
    print(f"Total Trades:        {len(trades)} ({len([t for t in trades if t['action'] == 'BUY'])} compras, {len(sell_trades)} ventas)")
    print(f"Trades Ganadores:    {len(winning_trades)}")
    print(f"Trades Perdedores:   {len(losing_trades)}")
    
    if sell_trades:
        avg_pnl = np.mean([t['pnl'] for t in sell_trades])
        avg_pnl_pct = np.mean([t['pnl_pct'] for t in sell_trades])
        
        if len(winning_trades) > 0:
            win_rate = (len(winning_trades) / len(sell_trades)) * 100
            print(f"Win Rate:            {Fore.GREEN}{win_rate:.1f}%{Style.RESET_ALL}")
        
        if avg_pnl > 0:
            print(f"P&L Promedio:        {Fore.GREEN}+${avg_pnl:,.2f} (+{avg_pnl_pct:.2f}%){Style.RESET_ALL}")
        else:
            print(f"P&L Promedio:        {Fore.RED}${avg_pnl:,.2f} ({avg_pnl_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📝 TRADES EJECUTADOS:{Style.RESET_ALL}")
    for trade in trades[:30]:  # Mostrar primeros 30
        action_color = Fore.GREEN if trade['action'] == 'BUY' else Fore.RED
        pnl_str = ""
        if trade['action'] == 'SELL' and 'pnl' in trade:
            pnl_color = Fore.GREEN if trade['pnl'] > 0 else Fore.RED
            pnl_str = f"| P&L: {pnl_color}{trade['pnl']:+.2f} ({trade['pnl_pct']:+.2f}%){Style.RESET_ALL}"
        
        print(f"{action_color}{trade['action']:<6}{Style.RESET_ALL} "
              f"{trade['date'].strftime('%Y-%m-%d')} | "
              f"{trade['shares']:>4} acciones @ ${trade['price']:.2f} | "
              f"{trade['reason']} {pnl_str}")
    
    if len(trades) > 30:
        print(f"... ({len(trades) - 30} trades más)")
    
    return {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'return_pct': return_pct,
        'buy_hold_return': buy_hold_return,
        'buy_hold_pct': buy_hold_pct,
        'outperformance': return_pct - buy_hold_pct,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'trades': trades
    }

    """
    Backtesting usando el AGENTE COMPLETO
    
    El agente analiza semanalmente usando los 16 factores y decide:
    - COMPRA/FUERTE COMPRA: Comprar si no tenemos posición
    - VENTA/FUERTE VENTA: Vender si tenemos posición
    - NEUTRAL: Hold
    
    Args:
        ticker: Símbolo de la acción
        start_date: Fecha inicial (default: hace 1 año)
        end_date: Fecha final (default: hoy)
        initial_capital: Capital inicial
    
    Returns:
        dict con resultados del backtest
    """
    # Defaults: último año
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"BACKTESTING CON AGENTE COMPLETO: {ticker}")
    print(f"Período: {start_date} a {end_date}")
    print(f"Capital Inicial: ${initial_capital:,.2f}")
    print(f"Análisis: Semanal (16 factores)")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Variables de trading
    cash = initial_capital
    shares = 0
    buy_price = 0
    trades = []
    
    # Generar fechas de análisis (semanal)
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    analysis_dates = []
    current_date = start
    while current_date <= end:
        analysis_dates.append(current_date)
        current_date += timedelta(days=7)
    
    print(f"Ejecutando {len(analysis_dates)} análisis semanales...\n")
    
    # Descargar datos históricos completos una vez
    print("Descargando datos históricos...")
    t = market_data.get_ticker_data(ticker)
    full_df = t.history(start=start_date, end=end_date)
    
    if full_df.empty:
        print(f"{Fore.RED}No se pudieron obtener datos históricos{Style.RESET_ALL}")
        return {"error": "No data"}
    
    # Iterar por fechas de análisis
    for i, analysis_date in enumerate(analysis_dates):
        date_str = analysis_date.strftime('%Y-%m-%d')
        print(f"[{i+1}/{len(analysis_dates)}] {date_str}...", end=" ")
        
        # Obtener precio del día más cercano
        try:
            # Convertir timezone-aware si es necesario
            if full_df.index.tz is not None:
                analysis_date_tz = analysis_date.tz_localize(full_df.index.tz) if analysis_date.tz is None else analysis_date
            else:
                analysis_date_tz = analysis_date.tz_localize(None) if analysis_date.tz is not None else analysis_date
            
            # Buscar fecha más cercana <=  analysis_date
            available_dates = full_df.index[full_df.index <= analysis_date_tz]
            if len(available_dates) == 0:
                print(f"{Fore.YELLOW}Skip (sin datos históricos aún){Style.RESET_ALL}")
                continue
            
            closest_date = available_dates[-1]
            price = full_df.loc[closest_date, 'Close']
        except Exception as e:
            print(f"{Fore.YELLOW}Skip (error: {str(e)[:30]}){Style.RESET_ALL}")
            continue
        
        # Ejecutar análisis del agente
        try:
            agent = FinancialAgent(ticker)
            results = agent.run_analysis()
            
            if "error" in results:
                print(f"{Fore.RED}Error{Style.RESET_ALL}")
                continue
            
            verdict = results['strategy']['verdict']
            confidence = results['strategy']['confidence']
            
            # Decisión de trading basada en el VEREDICTO DEL AGENTE
            if "COMPRA" in verdict:  # COMPRA o FUERTE COMPRA
                if shares == 0 and cash > price:
                    # Comprar con 95% del cash
                    shares_to_buy = int(cash * 0.95 / price)
                    if shares_to_buy > 0:
                        cost = shares_to_buy * price
                        shares += shares_to_buy
                        cash -= cost
                        buy_price = price
                        
                        trades.append({
                            'date': analysis_date,
                            'action': 'BUY',
                            'price': price,
                            'shares': shares_to_buy,
                            'cost': cost,
                            'verdict': verdict,
                            'confidence': confidence
                        })
                        print(f"{Fore.GREEN}COMPRA: {shares_to_buy} acciones @ ${price:.2f} ({verdict}){Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}HOLD (cash insuficiente){Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}HOLD (ya tenemos posición){Style.RESET_ALL}")
            
            elif "VENTA" in verdict:  # VENTA o FUERTE VENTA
                if shares > 0:
                    proceeds = shares * price
                    pnl = proceeds - (shares * buy_price)
                    pnl_pct = ((price - buy_price) / buy_price) * 100
                    
                    trades.append({
                        'date': analysis_date,
                        'action': 'SELL',
                        'price': price,
                        'shares': shares,
                        'proceeds': proceeds,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'verdict': verdict,
                        'confidence': confidence
                    })
                    
                    cash += proceeds
                    print(f"{Fore.RED}VENTA: {shares} acciones @ ${price:.2f} | P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%){Style.RESET_ALL}")
                    shares = 0
                    buy_price = 0
                else:
                    print(f"{Fore.YELLOW}HOLD (sin posición){Style.RESET_ALL}")
            
            else:  # NEUTRAL
                print(f"{Fore.CYAN}HOLD (NEUTRAL){Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)[:50]}{Style.RESET_ALL}")
            continue
    
    # Cerrar posición final si existe
    final_price = full_df['Close'].iloc[-1]
    if shares > 0:
        proceeds = shares * final_price
        pnl = proceeds - (shares * buy_price)
        pnl_pct = ((final_price - buy_price) / buy_price) * 100
        
        trades.append({
            'date': full_df.index[-1],
            'action': 'SELL',
            'price': final_price,
            'shares': shares,
            'proceeds': proceeds,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'verdict': 'Cierre final',
            'confidence': 0
        })
        
        cash += proceeds
        shares = 0
    
    # Calcular resultados
    final_value = cash + (shares * final_price)
    total_return = final_value - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    # Buy & Hold comparison
    initial_price = full_df['Close'].iloc[0]
    buy_hold_shares = initial_capital / initial_price
    buy_hold_value = buy_hold_shares * final_price
    buy_hold_return = buy_hold_value - initial_capital
    buy_hold_pct = (buy_hold_return / initial_capital) * 100
    
    # Estadísticas de trades
    sell_trades = [t for t in trades if t['action'] == 'SELL' and 'pnl' in t]
    winning_trades = [t for t in sell_trades if t['pnl'] > 0]
    losing_trades = [t for t in sell_trades if t['pnl'] < 0]
    
    # Imprimir resultados
    print(f"\n{Fore.CYAN}{'='*80}")
    print("RESULTADOS DEL BACKTESTING")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"📊 PERFORMANCE")
    print(f"Capital Inicial:     ${initial_capital:,.2f}")
    print(f"Capital Final:       ${final_value:,.2f}")
    
    if total_return > 0:
        print(f"Ganancia/Pérdida:    {Fore.GREEN}+${total_return:,.2f} (+{return_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Ganancia/Pérdida:    {Fore.RED}${total_return:,.2f} ({return_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n💼 POSICIÓN FINAL")
    print(f"Acciones:            {shares}")
    print(f"Cash:                ${cash:,.2f}")
    
    print(f"\n{Fore.YELLOW}📈 COMPARACIÓN: Buy & Hold{Style.RESET_ALL}")
    print(f"Valor Buy & Hold:    ${buy_hold_value:,.2f}")
    
    if buy_hold_return > 0:
        print(f"Retorno Buy & Hold:  {Fore.GREEN}+${buy_hold_return:,.2f} (+{buy_hold_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Retorno Buy & Hold:  {Fore.RED}${buy_hold_return:,.2f} ({buy_hold_pct:.2f}%){Style.RESET_ALL}")
    
    if return_pct > buy_hold_pct:
        diff = return_pct - buy_hold_pct
        print(f"\n{Fore.GREEN}✅ El agente SUPERÓ a Buy & Hold por {diff:.2f}%{Style.RESET_ALL}")
    else:
        diff = buy_hold_pct - return_pct
        print(f"\n{Fore.RED}❌ Buy & Hold fue mejor por {diff:.2f}%{Style.RESET_ALL}")
    
    # Estadísticas de trades
    print(f"\n📋 ESTADÍSTICAS DE TRADING")
    print(f"Total Trades:        {len(trades)} ({len([t for t in trades if t['action'] == 'BUY'])} compras, {len(sell_trades)} ventas)")
    print(f"Trades Ganadores:    {len(winning_trades)}")
    print(f"Trades Perdedores:   {len(losing_trades)}")
    
    if sell_trades:
        avg_pnl = np.mean([t['pnl'] for t in sell_trades])
        avg_pnl_pct = np.mean([t['pnl_pct'] for t in sell_trades])
        
        if len(winning_trades) > 0:
            win_rate = (len(winning_trades) / len(sell_trades)) * 100
            print(f"Win Rate:            {Fore.GREEN}{win_rate:.1f}%{Style.RESET_ALL}")
        
        if avg_pnl > 0:
            print(f"P&L Promedio:        {Fore.GREEN}+${avg_pnl:,.2f} (+{avg_pnl_pct:.2f}%){Style.RESET_ALL}")
        else:
            print(f"P&L Promedio:        {Fore.RED}${avg_pnl:,.2f} ({avg_pnl_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📝 TRADES EJECUTADOS:{Style.RESET_ALL}")
    for trade in trades[:30]:  # Mostrar primeros 30
        action_color = Fore.GREEN if trade['action'] == 'BUY' else Fore.RED
        pnl_str = ""
        if trade['action'] == 'SELL' and 'pnl' in trade:
            pnl_color = Fore.GREEN if trade['pnl'] > 0 else Fore.RED
            pnl_str = f"| P&L: {pnl_color}{trade['pnl']:+.2f} ({trade['pnl_pct']:+.2f}%){Style.RESET_ALL}"
        
        verdict_short = trade['verdict'][:30] if len(trade['verdict']) > 30 else trade['verdict']
        
        print(f"{action_color}{trade['action']:<6}{Style.RESET_ALL} "
              f"{trade['date'].strftime('%Y-%m-%d')} | "
              f"{trade['shares']:>4} @ ${trade['price']:.2f} | "
              f"{verdict_short} {pnl_str}")
    
    if len(trades) > 30:
        print(f"... ({len(trades) - 30} trades más)")
    
    return {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'return_pct': return_pct,
        'buy_hold_return': buy_hold_return,
        'buy_hold_pct': buy_hold_pct,
        'outperformance': return_pct - buy_hold_pct,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'trades': trades
    }

    """
    Backtesting simple usando reglas de trading basadas en indicadores
    
    Reglas de Trading:
    - COMPRA: RSI < 35 Y precio > SMA200
    - VENTA: RSI > 70 O pérdida > 10% O ganancia > 20%
    - HOLD: En cualquier otro caso
    
    Args:
        ticker: Símbolo de la acción
        start_date: Fecha inicial
        end_date: Fecha final
        initial_capital: Capital inicial
    
    Returns:
        dict con resultados del backtest
    """
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"BACKTESTING SIMPLE: {ticker}")
    print(f"Período: {start_date} a {end_date}")
    print(f"Capital Inicial: ${initial_capital:,.2f}")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Descargar datos históricos
    print("Descargando datos históricos...")
    t = market_data.get_ticker_data(ticker)
    
    # Usar yfinance directamente para obtener datos con fechas específicas
    df = t.history(start=start_date, end=end_date)
    
    if df.empty:
        return {"error": "No se pudieron obtener datos históricos"}
    
    # Calcular indicadores
    print("Calculando indicadores técnicos...")
    df = indicators.add_all_indicators(df)
    
    # Variables de trading
    cash = initial_capital
    shares = 0
    buy_price = 0
    trades = []
    
    # Iterar por cada día
    for i in range(200, len(df)):  # Empezar después de SMA200
        date = df.index[i]
        price = df['Close'].iloc[i]
        rsi = df['RSI'].iloc[i]
        sma_200 = df['SMA_200'].iloc[i]
        
        # Skip si hay NaN
        if pd.isna(rsi) or pd.isna(sma_200):
            continue
        
        # Señal de COMPRA
        if shares == 0 and cash > price:
            if rsi < 35 and price > sma_200:  # Oversold en tendencia alcista
                shares_to_buy = int(cash * 0.95 / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    shares += shares_to_buy
                    cash -= cost
                    buy_price = price
                    
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'cost': cost,
                        'rsi': rsi,
                        'reason': f'RSI Oversold ({rsi:.1f})'
                    })
        
        # Señal de VENTA
        elif shares > 0:
            pnl_pct = ((price - buy_price) / buy_price) * 100
            
            should_sell = False
            reason = ""
            
            if rsi > 70:
                should_sell = True
                reason = f"RSI Overbought ({rsi:.1f})"
            elif pnl_pct < -10:
                should_sell = True
                reason = f"Stop Loss ({pnl_pct:.1f}%)"
            elif pnl_pct > 20:
                should_sell = True
                reason = f"Take Profit ({pnl_pct:.1f}%)"
            
            if should_sell:
                proceeds = shares * price
                cash += proceeds
                
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': price,
                    'shares': shares,
                    'proceeds': proceeds,
                    'pnl': proceeds - (shares * buy_price),
                    'pnl_pct': pnl_pct,
                    'rsi': rsi,
                    'reason': reason
                })
                
                shares = 0
                buy_price = 0
    
    # Cerrar posición final si existe
    final_price = df['Close'].iloc[-1]
    if shares > 0:
        proceeds = shares * final_price
        pnl_pct = ((final_price - buy_price) / buy_price) * 100
        
        trades.append({
            'date': df.index[-1],
            'action': 'SELL',
            'price': final_price,
            'shares': shares,
            'proceeds': proceeds,
            'pnl': proceeds - (shares * buy_price),
            'pnl_pct': pnl_pct,
            'rsi': df['RSI'].iloc[-1],
            'reason': 'Cierre final'
        })
        
        cash += proceeds
        shares = 0
    
    # Calcular resultados
    final_value = cash + (shares * final_price)
    total_return = final_value - initial_capital
    return_pct = (total_return / initial_capital) * 100
    
    # Buy & Hold comparison
    initial_price = df['Close'].iloc[200]
    buy_hold_shares = initial_capital / initial_price
    buy_hold_value = buy_hold_shares * final_price
    buy_hold_return = buy_hold_value - initial_capital
    buy_hold_pct = (buy_hold_return / initial_capital) * 100
    
    # Estadísticas de trades
    winning_trades = [t for t in trades if t['action'] == 'SELL' and t.get('pnl', 0) > 0]
    losing_trades = [t for t in trades if t['action'] == 'SELL' and t.get('pnl', 0) < 0]
    
    # Imprimir resultados
    print(f"\n{Fore.CYAN}{'='*80}")
    print("RESULTADOS DEL BACKTESTING")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    print(f"📊 PERFORMANCE")
    print(f"Capital Inicial:     ${initial_capital:,.2f}")
    print(f"Capital Final:       ${final_value:,.2f}")
    
    if total_return > 0:
        print(f"Ganancia/Pérdida:    {Fore.GREEN}+${total_return:,.2f} (+{return_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Ganancia/Pérdida:    {Fore.RED}${total_return:,.2f} ({return_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n💼 POSICIÓN FINAL")
    print(f"Acciones:            {shares}")
    print(f"Cash:                ${cash:,.2f}")
    
    print(f"\n{Fore.YELLOW}📈 COMPARACIÓN: Buy & Hold{Style.RESET_ALL}")
    print(f"Valor Buy & Hold:    ${buy_hold_value:,.2f}")
    
    if buy_hold_return > 0:
        print(f"Retorno Buy & Hold:  {Fore.GREEN}+${buy_hold_return:,.2f} (+{buy_hold_pct:.2f}%){Style.RESET_ALL}")
    else:
        print(f"Retorno Buy & Hold:  {Fore.RED}${buy_hold_return:,.2f} ({buy_hold_pct:.2f}%){Style.RESET_ALL}")
    
    if return_pct > buy_hold_pct:
        diff = return_pct - buy_hold_pct
        print(f"\n{Fore.GREEN}✅ La estrategia SUPERÓ a Buy & Hold por {diff:.2f}%{Style.RESET_ALL}")
    else:
        diff = buy_hold_pct - return_pct
        print(f"\n{Fore.RED}❌ Buy & Hold fue mejor por {diff:.2f}%{Style.RESET_ALL}")
    
    # Estadísticas de trades
    sell_trades = [t for t in trades if t['action'] == 'SELL' and 'pnl' in t]
    
    print(f"\n📋 ESTADÍSTICAS DE TRADING")
    print(f"Total Trades:        {len(trades)} ({len([t for t in trades if t['action'] == 'BUY'])} compras, {len(sell_trades)} ventas)")
    print(f"Trades Ganadores:    {len(winning_trades)}")
    print(f"Trades Perdedores:   {len(losing_trades)}")
    
    if sell_trades:
        avg_pnl = np.mean([t['pnl'] for t in sell_trades])
        avg_pnl_pct = np.mean([t['pnl_pct'] for t in sell_trades])
        
        if avg_pnl > 0:
            print(f"P&L Promedio:        {Fore.GREEN}+${avg_pnl:,.2f} (+{avg_pnl_pct:.2f}%){Style.RESET_ALL}")
        else:
            print(f"P&L Promedio:        {Fore.RED}${avg_pnl:,.2f} ({avg_pnl_pct:.2f}%){Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📝 TRADES EJECUTADOS:{Style.RESET_ALL}")
    for trade in trades[:20]:  # Mostrar primeros 20
        action_color = Fore.GREEN if trade['action'] == 'BUY' else Fore.RED
        pnl_str = ""
        if trade['action'] == 'SELL' and 'pnl' in trade:
            pnl_color = Fore.GREEN if trade['pnl'] > 0 else Fore.RED
            pnl_str = f"| P&L: {pnl_color}{trade['pnl']:+.2f} ({trade['pnl_pct']:+.2f}%){Style.RESET_ALL}"
        
        print(f"{action_color}{trade['action']:<6}{Style.RESET_ALL} "
              f"{trade['date'].strftime('%Y-%m-%d')} | "
              f"{trade['shares']:>4} acciones @ ${trade['price']:.2f} | "
              f"{trade['reason']} {pnl_str}")
    
    if len(trades) > 20:
        print(f"... ({len(trades) - 20} trades más)")
    
    return {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'return_pct': return_pct,
        'buy_hold_return': buy_hold_return,
        'buy_hold_pct': buy_hold_pct,
        'outperformance': return_pct - buy_hold_pct,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'trades': trades
    }
