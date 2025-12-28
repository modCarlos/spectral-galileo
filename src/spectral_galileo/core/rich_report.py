"""
Rich-based report generator for beautiful console output.
Replaces colorama-based formatting with Rich library components.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.rule import Rule
import io


def generate_rich_report(analysis_results, is_short_term=False, full_analysis=False):
    """
    Generate a beautiful financial analysis report using Rich library.
    
    Args:
        analysis_results: The analysis results dictionary
        is_short_term: Whether this is a short-term analysis
        full_analysis: Whether to show complete analysis or basic mode
        
    Returns:
        String representation of the formatted report
    """
    res = analysis_results
    
    # Create console with string capture
    string_io = io.StringIO()
    console = Console(file=string_io, force_terminal=True, width=100)
    
    # ═══════════════════════════════════════════════════════════════
    # GENERATE HUMAN NARRATIVE
    # ═══════════════════════════════════════════════════════════════
    verdict = res['strategy']['verdict']
    horizon = res['strategy']['horizon']
    
    human_analysis = _generate_human_analysis(res, is_short_term)
    
    # Add tactical summary and benchmarks
    adx_val = res['technical']['adx']
    mkt_env = res['technical']['market_env']
    summary_line = f"\n📌 RESUMEN TÁCTICO: {res['symbol']}: {mkt_env} (ADX {adx_val:.0f}) -> {verdict}"
    
    benchmarks = (
        "\n\n💡 GUÍA DE REFERENCIA (Benchmarks):\n"
        "  • NVDA: Tech Explosivo -> FUERTE COMPRA🚀 (RSI oversold + MACD bullish)\n"
        "  • META: Mega-Cap -> Umbrales ultra-conservadores (35/65)\n"
        "  • PLTR: High-Vol -> Umbrales ajustados (43/57)\n"
        "  • AAPL: Blue-Chip -> Scoring balanceado (42/58)"
    )
    human_analysis += summary_line + benchmarks

    horizon_label = "CORTO PLAZO (3-6 Meses)" if is_short_term else "LARGO PLAZO (3-5 Años)"
    
    # ═══════════════════════════════════════════════════════════════
    # HEADER WITH RICH PANEL
    # ═══════════════════════════════════════════════════════════════
    _print_header(console, res, horizon_label)
    
    # ═══════════════════════════════════════════════════════════════
    # PERSONAL OPINION PANEL
    # ═══════════════════════════════════════════════════════════════
    _print_opinion(console, human_analysis)
    
    # ═══════════════════════════════════════════════════════════════
    # TECHNICAL ANALYSIS TABLE - ONLY IN FULL MODE
    # ═══════════════════════════════════════════════════════════════
    if full_analysis:
        _print_technical_analysis(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # VERDICT & STRATEGY TABLE
    # ═══════════════════════════════════════════════════════════════
    _print_verdict_table(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # ADVANCED ANALYSIS - ONLY IN FULL MODE
    # ═══════════════════════════════════════════════════════════════
    if full_analysis and res.get('advanced'):
        _print_advanced_analysis(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # TREND ANALYSIS (when NEUTRAL/HOLD)
    # ═══════════════════════════════════════════════════════════════
    _print_trend_analysis(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # PROS & CONS
    # ═══════════════════════════════════════════════════════════════
    _print_pros_cons(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # RISK/REWARD RATIO
    # ═══════════════════════════════════════════════════════════════
    _print_risk_reward(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # DECISION GUIDE
    # ═══════════════════════════════════════════════════════════════
    _print_decision_guide(console, res)
    
    # ═══════════════════════════════════════════════════════════════
    # FUNDAMENTALS - ONLY IN FULL MODE
    # ═══════════════════════════════════════════════════════════════
    if full_analysis:
        _print_fundamentals(console, res)
        _print_dividends(console, res)
        _print_sentiment(console, res)
        _print_macro(console, res)
        _print_key_levels(console, res)
        _print_alternatives(console, res)
    
    # Message for full analysis
    if not full_analysis:
        console.print()
        console.print(Rule(style="yellow dim"))
        console.print(
            f"[yellow]💡 Para ver el análisis técnico completo, usa: [cyan bold]python main.py {res['ticker']} -f[/]\n"
            "[dim](Incluye: técnicos detallados, fundamentos, dividendos, sentimiento, macro, niveles clave)[/]",
            justify="center"
        )
    
    # Return the captured string
    return string_io.getvalue()


def _generate_human_analysis(res, is_short_term):
    """Generate human-readable analysis narrative."""
    verdict = res['strategy']['verdict']
    
    if is_short_term:
        if "FUERTE COMPRA" in verdict or "COMPRA" in verdict:
            return (
                f"A corto plazo (3-6 meses), veo a {res['symbol']} con un momentum muy favorable. "
                "Los indicadores técnicos sugieren que la presión de compra está aumentando. "
                "Es una oportunidad excelente para un trade táctico, buscando capturar el próximo impulso. "
                "Mantén un ojo en los niveles de resistencia de corto plazo."
            )
        elif "VENTA" in verdict or "FUERTE VENTA" in verdict:
            return (
                f"Precaución extrema con {res['symbol']} para los próximos 3-6 meses. "
                "El momentum es claramente bajista y el riesgo de una corrección mayor es alto. "
                "No es momento de buscar rebotes todavía; la estructura de mercado está dañada. "
                "Considera reducir exposición para proteger capital táctico."
            )
        else:
            return (
                f"Para un horizonte de 3-6 meses, {res['symbol']} se encuentra en una fase de consolidación. "
                "No hay una tendencia clara a explotar en este momento. "
                "Sugiero esperar a que el precio rompa con volumen alguno de los niveles clave antes de entrar. "
                "Paciencia estratégica es la clave aquí."
            )
    else:
        if "FUERTE COMPRA" in verdict:
            return (
                f"Según mi análisis, {res['symbol']} es una candidata excelente para tu portafolio. "
                "Muestra una alineación sólida entre técnicos y fundamentales. "
                "Es un momento ideal para compras pensando en el largo plazo (3-5 años)."
            )
        elif "COMPRA" in verdict:
            return (
                "Es un buen punto de entrada. La empresa tiene fundamentos decentes y el precio acompaña. "
                "Podrías iniciar una posición escalonada ahora y añadir más si baja a los soportes indicados."
            )
        elif "VENTA" in verdict:
            return (
                "Sinceramente, no veo esto bien. Los indicadores apuntan a una caída o corrección. "
                "Si tienes ganancias, considera tomarlas ahora. Si buscas comprar, es mejor tener paciencia "
                "y esperar niveles más bajos. "
                f"Si ya eres holder, te sugiero ajustar tu Stop Loss a ${res['strategy']['stop_loss']:.2f} para proteger capital."
            )
        else:
            return (
                "El escenario está muy indeciso. No hay una ventaja clara. "
                "Personalmente, no arriesgaría capital aquí todavía. Mejor espera a que rompa una resistencia clave "
                "o busca alternativas con tendencias más definidas en el sector. "
                f"Si ya tienes acciones, considera vender si baja de ${res['strategy']['stop_loss']:.2f}."
            )


def _print_header(console, res, horizon_label):
    """Print beautiful header panel."""
    price_above_sma = res['current_price'] > res['technical'].get('sma_200', 0)
    price_color = "green" if price_above_sma else "red"
    price_trend = "↗" if price_above_sma else "↘"
    
    header_text = Text()
    header_text.append("📊 ANÁLISIS FINANCIERO\n\n", style="bold cyan")
    header_text.append(f"{res['symbol']}", style="bold white")
    header_text.append(f" • ", style="dim")
    header_text.append(f"${res['current_price']:.2f} {price_trend}", style=f"bold {price_color}")
    header_text.append(f"\n{horizon_label}", style="yellow")
    
    console.print(Panel(header_text, border_style="cyan", box=box.DOUBLE))
    console.print()


def _print_opinion(console, human_analysis):
    """Print personal opinion panel."""
    opinion_panel = Panel(
        human_analysis,
        title="[bold magenta]🤖 MI OPINIÓN PERSONAL[/]",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(opinion_panel)
    console.print()


def _print_technical_analysis(console, res):
    """Print technical indicators table."""
    tech_table = Table(title="📈 ANÁLISIS TÉCNICO", box=box.ROUNDED, border_style="cyan", show_header=True)
    tech_table.add_column("Indicador", style="white bold", no_wrap=True)
    tech_table.add_column("Valor", style="cyan", justify="right")
    tech_table.add_column("Estado", style="bold", justify="center")
    
    # RSI
    rsi = res['technical']['rsi']
    if rsi > 70:
        rsi_status, rsi_style = "🔴 Sobrecompra", "red"
    elif rsi < 30:
        rsi_status, rsi_style = "🟢 Sobreventa", "green"
    else:
        rsi_status, rsi_style = "⚪ Neutral", "yellow"
    tech_table.add_row("RSI (14)", f"{rsi:.2f}", f"[{rsi_style}]{rsi_status}[/]")
    
    # Trend (SMA 200)
    sma200 = res['technical']['sma_200']
    trend = "Alcista ↗" if res['current_price'] > sma200 else "Bajista ↘"
    trend_style = "green" if res['current_price'] > sma200 else "red"
    tech_table.add_row("Tendencia (SMA200)", f"${sma200:.2f}", f"[{trend_style}]{trend}[/]")
    
    # MACD
    macd_status = res['technical']['macd_status']
    if "Bullish" in macd_status:
        macd_style, macd_icon = "green", "🟢"
    elif "Bearish" in macd_status:
        macd_style, macd_icon = "red", "🔴"
    else:
        macd_style, macd_icon = "yellow", "⚪"
    tech_table.add_row("MACD", f"[{macd_style}]{macd_icon} {macd_status}[/]", "")
    
    # Stochastic
    stoch_k = res['technical']['stoch_k']
    if stoch_k > 80:
        stoch_status, stoch_style = "🔴 Sobrecompra", "red"
    elif stoch_k < 20:
        stoch_status, stoch_style = "🟢 Sobreventa", "green"
    else:
        stoch_status, stoch_style = "⚪ Neutral", "yellow"
    tech_table.add_row("Estocástico K", f"{stoch_k:.2f}", f"[{stoch_style}]{stoch_status}[/]")
    
    # ADX
    adx = res['technical']['adx']
    if adx > 25:
        adx_status, adx_style = "💪 Tendencia Fuerte", "green"
    else:
        adx_status, adx_style = "😴 Tendencia Débil", "yellow"
    tech_table.add_row("ADX", f"{adx:.2f}", f"[{adx_style}]{adx_status}[/]")
    
    # Market Environment
    mkt_env = res['technical']['market_env']
    tech_table.add_row("Entorno", mkt_env, "")
    
    console.print(tech_table)
    console.print()


def _print_verdict_table(console, res):
    """Print verdict and strategy table."""
    verdict_text = res['strategy']['verdict']
    confidence = res['strategy']['confidence']
    
    # Determine verdict styling
    if "FUERTE COMPRA" in verdict_text:
        verdict_style, verdict_emoji = "bold green", "🚀"
    elif "COMPRA" in verdict_text:
        verdict_style, verdict_emoji = "green", "🟢"
    elif "VENTA" in verdict_text:
        verdict_style, verdict_emoji = "red", "🔴"
    else:
        verdict_style, verdict_emoji = "yellow", "⚪"
    
    # Confidence styling
    if confidence >= 60:
        conf_style = "bold green"
    elif confidence >= 40:
        conf_style = "yellow"
    else:
        conf_style = "red"
    
    strategy_table = Table(
        title="🎯 ESTRATEGIA & VEREDICTO",
        box=box.HEAVY,
        border_style="green",
        show_header=False,
        padding=(0, 1)
    )
    strategy_table.add_column("Item", style="white bold", width=20)
    strategy_table.add_column("Detalle", style="cyan")
    
    strategy_table.add_row(
        "VEREDICTO",
        f"[{verdict_style}]{verdict_emoji} {verdict_text}[/]"
    )
    strategy_table.add_row(
        "CONFIANZA",
        f"[{conf_style}]{confidence:.0f}%[/]"
    )
    
    prob_success = res['strategy'].get('probability_success')
    if prob_success is not None:
        strategy_table.add_row("PROBABILIDAD", f"{prob_success:.1f}%")
    
    strategy_table.add_row("HORIZONTE", res['strategy']['horizon'])
    strategy_table.add_row("RIESGO/BENEFICIO", f"{res['strategy']['risk_reward']:.2f}")
    strategy_table.add_row("STOP LOSS", f"[red]${res['strategy']['stop_loss']:.2f}[/]")
    
    # Target can be short_term or mid_term depending on horizon
    target_price = res['strategy'].get('sell_levels', {}).get('short_term', res['current_price'] * 1.10)
    strategy_table.add_row("OBJETIVO", f"[green]${target_price:.2f}[/]")
    
    # Suggested action
    action_suggested = "Esperar / Observar"
    action_style = "yellow"
    if "COMPRA" in res['strategy']['verdict']:
        action_suggested = "Considerar Abrir Posición (Largo)"
        action_style = "green"
    elif "VENTA" in res['strategy']['verdict']:
        action_suggested = "Considerar Cerrar Posición / Vender"
        action_style = "red"
    
    strategy_table.add_row("ACCIÓN SUGERIDA", f"[{action_style}]{action_suggested}[/]")
    
    console.print(strategy_table)
    console.print()


def _print_advanced_analysis(console, res):
    """Print advanced analysis section."""
    adv = res['advanced']
    
    # Multi-Timeframe Analysis
    if adv.get('multi_timeframe') and adv['multi_timeframe'].get('confluence'):
        console.print("[bold cyan]📊 Análisis Multi-Timeframe[/]")
        mtf = adv['multi_timeframe']
        conf = mtf['confluence']
        signals = mtf['signals']
        
        mtf_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        mtf_table.add_column("Period", style="dim")
        mtf_table.add_column("Signal")
        
        mtf_table.add_row("Daily", signals.get('daily', 'N/A'))
        mtf_table.add_row("Weekly", signals.get('weekly', 'N/A'))
        mtf_table.add_row("Monthly", signals.get('monthly', 'N/A'))
        mtf_table.add_row("", "")
        mtf_table.add_row("[bold]Confluencia", f"[bold]{conf['score']:.0f}% ({conf['strength']})[/]")
        mtf_table.add_row("[bold]Señal General", f"[bold]{conf['overall_signal']}[/]")
        
        console.print(mtf_table)
        console.print()
    
    # Market Regime
    if adv.get('market_regime'):
        regime = adv['market_regime']
        console.print(f"[bold cyan]🌍 Régimen de Mercado:[/] {regime['regime']} ([green]{regime['confidence']:.0f}%[/] confianza)")
        console.print(f"[dim]{regime['description']}[/]")
        console.print()
    
    # Reddit Sentiment
    if adv.get('reddit_sentiment') and adv['reddit_sentiment'].get('available'):
        _print_reddit_sentiment(console, adv['reddit_sentiment'])
    
    # Earnings Calendar
    if adv.get('earnings_calendar') and adv['earnings_calendar'].get('available'):
        _print_earnings(console, adv['earnings_calendar'])
    
    # Insider Trading
    if adv.get('insider_trading') and adv['insider_trading'].get('available'):
        _print_insider(console, adv['insider_trading'])
    
    # Confluence Score
    if adv.get('confluence_score') is not None:
        console.print(f"[bold yellow]✨ Score de Confluencia: {adv['confluence_score']:.0f}%[/]")
        if adv.get('aligned_signals'):
            console.print(f"   Señales alineadas: {len(adv['aligned_signals'])}")
        console.print()


def _print_reddit_sentiment(console, reddit):
    """Print Reddit sentiment analysis."""
    if reddit['mentions'] > 0:
        emoji_map = {'BULLISH': '🚀', 'BEARISH': '🐻', 'NEUTRAL': '😐'}
        emoji = emoji_map.get(reddit['sentiment'], '❓')
        
        console.print(f"[bold cyan]📱 Reddit Sentiment (24h)[/]")
        reddit_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        reddit_table.add_column("Metric", style="dim")
        reddit_table.add_column("Value")
        
        reddit_table.add_row("Menciones", str(reddit['mentions']))
        reddit_table.add_row("Sentiment", f"{emoji} {reddit['sentiment']} ({reddit['score']:+.0f})")
        reddit_table.add_row("Engagement", f"{reddit['engagement']:.0f}/100")
        reddit_table.add_row("Upvotes", f"{reddit['total_upvotes']:,}")
        reddit_table.add_row("Comentarios", f"{reddit['total_comments']:,}")
        
        if reddit.get('top_posts') and len(reddit['top_posts']) > 0:
            top_post = reddit['top_posts'][0]
            reddit_table.add_row("Top Post", f"\"{top_post['title'][:50]}...\" ({top_post['score']}↑)")
        
        console.print(reddit_table)
        console.print()
    else:
        console.print("[dim]📱 Reddit Sentiment: Sin actividad reciente[/]")
        console.print()


def _print_earnings(console, earnings):
    """Print earnings calendar information."""
    console.print("[bold cyan]📅 Earnings Calendar[/]")
    
    earnings_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    earnings_table.add_column("Item", style="dim")
    earnings_table.add_column("Value")
    
    if earnings.get('days_to_earnings') is not None:
        days = earnings['days_to_earnings']
        if days < 0:
            earnings_table.add_row("Próximo", f"Ya reportado (hace {abs(days)} días)")
        elif days == 0:
            earnings_table.add_row("Próximo", "[red bold]⚠️ HOY[/]")
        elif days <= 7:
            earnings_table.add_row("Próximo", f"[yellow]⚠️ En {days} días (alta volatilidad)[/]")
        else:
            earnings_table.add_row("Próximo", f"En {days} días")
    
    if earnings.get('last_surprise_pct') is not None:
        surprise = earnings['last_surprise_pct']
        emoji = "✅" if surprise > 0 else "❌"
        earnings_table.add_row("Último", f"{emoji} {surprise:+.1f}% vs estimate")
    
    if earnings.get('earnings_trend') and earnings['earnings_trend'] != 'UNKNOWN':
        trend_emoji = {'BEATING': '📈', 'MISSING': '📉', 'MEETING': '➡️'}
        emoji = trend_emoji.get(earnings['earnings_trend'], '❓')
        earnings_table.add_row("Tendencia", f"{emoji} {earnings['earnings_trend']}")
        
        if earnings.get('beat_streak') and earnings['beat_streak'] > 0:
            earnings_table.add_row("Beat Streak", f"{earnings['beat_streak']}/4 quarters")
    
    console.print(earnings_table)
    console.print()


def _print_insider(console, insider):
    """Print insider trading activity."""
    if insider['total_transactions'] > 0:
        console.print("[bold cyan]👔 Insider Activity (90 days)[/]")
        
        insider_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        insider_table.add_column("Item", style="dim")
        insider_table.add_column("Value")
        
        buys = insider['buy_transactions']
        sells = insider['sell_transactions']
        insider_table.add_row("Transactions", f"{buys} buys, {sells} sells")
        
        net_value = insider.get('net_value', 0)
        if net_value > 1e6:
            insider_table.add_row("Net Activity", f"[green]📈 +${net_value/1e6:.1f}M buying[/]")
        elif net_value < -1e6:
            insider_table.add_row("Net Activity", f"[red]📉 ${net_value/1e6:.1f}M selling[/]")
        
        sentiment = insider['insider_sentiment']
        emoji_map = {'BULLISH': '🟢', 'BEARISH': '🔴', 'NEUTRAL': '⚪'}
        emoji = emoji_map.get(sentiment, '❓')
        insider_table.add_row("Sentiment", f"{emoji} {sentiment}")
        
        if insider.get('recent_large_buys') and len(insider['recent_large_buys']) > 0:
            top_buy = insider['recent_large_buys'][0]
            insider_table.add_row("Top Buy", f"{top_buy['insider']} (${abs(top_buy['value'])/1e3:.0f}K)")
        elif insider.get('recent_large_sells') and len(insider['recent_large_sells']) > 0:
            top_sell = insider['recent_large_sells'][0]
            insider_table.add_row("Top Sell", f"{top_sell['insider']} (${abs(top_sell['value'])/1e3:.0f}K)")
        
        console.print(insider_table)
        console.print()
    else:
        console.print("[dim]👔 Insider Activity: No recent transactions (90 days)[/]")
        console.print()


def _print_trend_analysis(console, res):
    """Print trend analysis for NEUTRAL/HOLD verdicts."""
    verdict_text = res['strategy']['verdict']
    if 'NEUTRAL' not in verdict_text and 'HOLD' not in verdict_text:
        return
    
    confidence_val = res['strategy']['confidence']
    buy_thresh = res['strategy'].get('buy_threshold')
    sell_thresh = res['strategy'].get('sell_threshold')
    
    if buy_thresh is None or sell_thresh is None:
        return
    
    console.print(Rule("[bold yellow]📊 ANÁLISIS DE TENDENCIA (Zona Neutral)[/]", style="yellow"))
    console.print()
    
    # Calculate distances
    dist_to_buy = abs(confidence_val - buy_thresh)
    dist_to_sell = abs(confidence_val - sell_thresh)
    
    # Determine tendency
    if dist_to_buy < dist_to_sell:
        tendency = "COMPRA"
        tendency_emoji = "🟢"
        tendency_style = "green"
        distance = dist_to_buy
    else:
        tendency = "VENTA"
        tendency_emoji = "🔴"
        tendency_style = "red"
        distance = dist_to_sell
    
    # Classify proximity
    if distance <= 3:
        proximity = "MUY CERCA"
        proximity_emoji = "⚠️"
        proximity_style = "red"
        advice = f"Podría cambiar a {tendency} con pequeñas variaciones del mercado"
    elif distance <= 7:
        proximity = "CERCA"
        proximity_emoji = "⚡"
        proximity_style = "yellow"
        advice = f"Observar de cerca - movimiento moderado podría cambiar señal a {tendency}"
    elif distance <= 15:
        proximity = "MODERADA"
        proximity_emoji = "📍"
        proximity_style = "cyan"
        advice = f"Posición neutral estable - necesitaría cambio significativo para {tendency}"
    else:
        proximity = "LEJOS"
        proximity_emoji = "🔵"
        proximity_style = "blue"
        advice = f"Posición muy neutral - poco probable cambio inmediato a {tendency}"
    
    # Position table
    pos_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    pos_table.add_column("Metric", style="dim")
    pos_table.add_column("Value")
    
    pos_table.add_row("Confianza Actual", f"[cyan]{confidence_val:.1f}%[/]")
    pos_table.add_row("Umbral COMPRA", f"[green]≥{buy_thresh:.1f}%[/]")
    pos_table.add_row("Umbral VENTA", f"[red]≤{sell_thresh:.1f}%[/]")
    pos_table.add_row("", "")
    pos_table.add_row(
        f"[{tendency_style}]Tendencia Detectada[/]",
        f"[{tendency_style}]{tendency_emoji} {tendency}[/]"
    )
    pos_table.add_row(
        f"[{proximity_style}]Distancia[/]",
        f"[{proximity_style}]{proximity_emoji} {distance:.1f} puntos - {proximity}[/]"
    )
    
    console.print(pos_table)
    console.print()
    
    # Interpretation
    console.print("[dim]💡 Interpretación:[/]")
    console.print(f"   • Distancia a {tendency}: [cyan]{distance:.1f} puntos[/]")
    if tendency == "COMPRA":
        console.print(f"   • Distancia a VENTA: [cyan]{dist_to_sell:.1f} puntos[/]")
    else:
        console.print(f"   • Distancia a COMPRA: [cyan]{dist_to_buy:.1f} puntos[/]")
    console.print()
    console.print(f"[{proximity_style}]{proximity_emoji} Recomendación:[/] {advice}")
    console.print()
    
    # Visual bar
    bar_length = 50
    filled = int((confidence_val / 100) * bar_length)
    buy_pos = int((buy_thresh / 100) * bar_length)
    sell_pos = int((sell_thresh / 100) * bar_length)
    
    bar = []
    for i in range(bar_length):
        if i == filled:
            bar.append("[yellow]●[/]")
        elif i == buy_pos:
            bar.append("[green]↑[/]")
        elif i == sell_pos:
            bar.append("[red]↓[/]")
        elif i < filled:
            bar.append("[cyan]━[/]")
        else:
            bar.append("[dim white]━[/]")
    
    console.print("[dim]Posición Visual:[/]")
    console.print(f"0% {''.join(bar)} 100%")
    console.print("   [red]↓=Venta[/]   [yellow]●=Actual[/]   [green]↑=Compra[/]")
    console.print()


def _print_pros_cons(console, res):
    """Print pros and cons."""
    # Pros
    console.print("[bold green]✅ POR QUÉ COMPRAR (Pros)[/]")
    if res['strategy']['pros']:
        for p in res['strategy']['pros']:
            console.print(f"  [green]+[/] {p}")
    else:
        console.print("  [dim](Ninguno destacado)[/]")
    console.print()
    
    # Cons
    console.print("[bold red]⚠️  POR QUÉ TENER CUIDADO (Contras)[/]")
    if res['strategy']['cons']:
        for c in res['strategy']['cons']:
            console.print(f"  [red]-[/] {c}")
    else:
        console.print("  [dim](Ninguno destacado)[/]")
    console.print()


def _print_risk_reward(console, res):
    """Print risk/reward ratio."""
    rr = res['strategy']['risk_reward']
    if rr < 1:
        rr_desc = "Malo - Riesgo mayor al beneficio"
        rr_style = "red"
    elif rr < 2:
        rr_desc = "Aceptable - Ganancia compensa riesgo"
        rr_style = "yellow"
    else:
        rr_desc = "Excelente - Potencial ganancia duplica riesgo"
        rr_style = "green"
    
    console.print(f"[bold cyan]⚖️  Ratio Riesgo/Beneficio:[/] [{rr_style}]{rr:.2f}[/]")
    console.print(f"[dim]{rr_desc}[/]")
    console.print(f"[dim]Por cada $1 arriesgado (hasta Stop Loss), se esperan ${rr:.2f} de ganancia (hasta Objetivo).[/]")
    console.print()


def _print_decision_guide(console, res):
    """Print practical decision guide."""
    console.print(Rule("[bold magenta]📋 GUÍA DE DECISIÓN PRÁCTICA[/]", style="magenta"))
    console.print()
    
    confidence = res['strategy']['confidence']
    
    if confidence >= 75:
        zone_info = {
            'emoji': '🟢',
            'name': 'ZONA VERDE',
            'style': 'green',
            'size': '100%',
            'action': 'Compra posición completa',
            'risk': 'Bajo - Señales fuertemente alineadas'
        }
    elif confidence >= 55:
        zone_info = {
            'emoji': '🟡',
            'name': 'ZONA AMARILLA',
            'style': 'yellow',
            'size': '50-75%',
            'action': 'Compra posición parcial',
            'risk': 'Moderado - Algunas señales mixtas'
        }
    elif confidence >= 30:
        zone_info = {
            'emoji': '⚠️',
            'name': 'ZONA GRIS',
            'style': 'yellow dim',
            'size': '25-50%',
            'action': 'Solo especulativo',
            'risk': 'Alto - Conflicto en señales'
        }
    else:
        zone_info = {
            'emoji': '🔴',
            'name': 'ZONA ROJA',
            'style': 'red',
            'size': '0%',
            'action': 'NO COMPRAR',
            'risk': 'Muy Alto - Evitar entrada'
        }
    
    guide_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    guide_table.add_column("Item", style="dim")
    guide_table.add_column("Detalle")
    
    guide_table.add_row(
        "Zona de Confianza",
        f"[{zone_info['style']}]{zone_info['emoji']} {zone_info['name']}[/]"
    )
    guide_table.add_row("Tamaño de Posición", zone_info['size'])
    guide_table.add_row("Acción", zone_info['action'])
    guide_table.add_row("Nivel de Riesgo", zone_info['risk'])
    
    console.print(guide_table)
    console.print()


def _print_fundamentals(console, res):
    """Print fundamental analysis."""
    if not res.get('fundamentals'):
        return
    
    fund = res['fundamentals']
    console.print(Rule("[bold cyan]📊 ANÁLISIS FUNDAMENTAL[/]", style="cyan"))
    console.print()
    
    fund_table = Table(box=box.ROUNDED, show_header=True, border_style="cyan")
    fund_table.add_column("Métrica", style="white")
    fund_table.add_column("Valor", style="cyan", justify="right")
    fund_table.add_column("Evaluación", style="bold")
    
    if fund.get('pe_ratio'):
        pe = fund['pe_ratio']
        if pe < 15:
            pe_eval = "[green]Barato[/]"
        elif pe < 25:
            pe_eval = "[yellow]Justo[/]"
        else:
            pe_eval = "[red]Caro[/]"
        fund_table.add_row("P/E Ratio", f"{pe:.2f}", pe_eval)
    
    if fund.get('peg_ratio'):
        peg = fund['peg_ratio']
        if peg < 1:
            peg_eval = "[green]Infravalorado[/]"
        elif peg < 2:
            peg_eval = "[yellow]Justo[/]"
        else:
            peg_eval = "[red]Sobrevalorado[/]"
        fund_table.add_row("PEG Ratio", f"{peg:.2f}", peg_eval)
    
    if fund.get('recommendation'):
        fund_table.add_row("Recomendación Analistas", fund['recommendation'], "")
    
    console.print(fund_table)
    console.print()


def _print_dividends(console, res):
    """Print dividend information."""
    if not res.get('dividends') or not res['dividends'].get('dividend_yield'):
        return
    
    div = res['dividends']
    console.print("[bold cyan]💰 DIVIDENDOS[/]")
    
    div_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    div_table.add_column("Item", style="dim")
    div_table.add_column("Value")
    
    yield_val = div['dividend_yield'] * 100
    if yield_val > 4:
        yield_style = "green"
    elif yield_val > 2:
        yield_style = "yellow"
    else:
        yield_style = "dim"
    div_table.add_row("Yield", f"[{yield_style}]{yield_val:.2f}%[/]")
    
    if div.get('payout_ratio'):
        payout = div['payout_ratio'] * 100
        if payout < 60:
            payout_style = "green"
        elif payout < 80:
            payout_style = "yellow"
        else:
            payout_style = "red"
        div_table.add_row("Payout Ratio", f"[{payout_style}]{payout:.1f}%[/]")
    
    console.print(div_table)
    console.print()


def _print_sentiment(console, res):
    """Print market sentiment."""
    if not res.get('sentiment'):
        return
    
    sent = res['sentiment']
    console.print("[bold cyan]📊 SENTIMIENTO DE MERCADO[/]")
    
    sent_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    sent_table.add_column("Metric", style="dim")
    sent_table.add_column("Value")
    
    if sent.get('overall'):
        overall = sent['overall']
        if overall == 'POSITIVE':
            sent_style = "green"
        elif overall == 'NEGATIVE':
            sent_style = "red"
        else:
            sent_style = "yellow"
        sent_table.add_row("General", f"[{sent_style}]{overall}[/]")
    
    if sent.get('score'):
        sent_table.add_row("Score", f"{sent['score']:.2f}/10")
    
    console.print(sent_table)
    console.print()


def _print_macro(console, res):
    """Print macroeconomic context."""
    if not res.get('macro'):
        return
    
    macro = res['macro']
    console.print("[bold cyan]🌍 CONTEXTO MACROECONÓMICO[/]")
    
    macro_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    macro_table.add_column("Indicator", style="dim")
    macro_table.add_column("Value")
    
    if macro.get('vix'):
        vix = macro['vix']
        if vix < 15:
            vix_desc = "[green]Baja volatilidad[/]"
        elif vix < 25:
            vix_desc = "[yellow]Volatilidad moderada[/]"
        else:
            vix_desc = "[red]Alta volatilidad[/]"
        macro_table.add_row("VIX", f"{vix:.2f} - {vix_desc}")
    
    if macro.get('fear_greed_index'):
        fgi = macro['fear_greed_index']
        if fgi < 25:
            fgi_desc = "[red]Miedo Extremo[/]"
        elif fgi < 45:
            fgi_desc = "[yellow]Miedo[/]"
        elif fgi < 55:
            fgi_desc = "[dim]Neutral[/]"
        elif fgi < 75:
            fgi_desc = "[green]Codicia[/]"
        else:
            fgi_desc = "[green bold]Codicia Extrema[/]"
        macro_table.add_row("Fear & Greed", f"{fgi} - {fgi_desc}")
    
    console.print(macro_table)
    console.print()


def _print_key_levels(console, res):
    """Print key price levels."""
    console.print("[bold cyan]🎯 NIVELES CLAVE[/]")
    
    levels_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    levels_table.add_column("Level", style="dim")
    levels_table.add_column("Price", style="cyan", justify="right")
    
    levels_table.add_row("[red]Stop Loss[/]", f"[red]${res['strategy']['stop_loss']:.2f}[/]")
    levels_table.add_row("Precio Actual", f"[white bold]${res['current_price']:.2f}[/]")
    
    # Show all sell levels as targets
    sell_levels = res['strategy'].get('sell_levels', {})
    if sell_levels.get('short_term'):
        levels_table.add_row("[green]Objetivo Corto[/]", f"[green]${sell_levels['short_term']:.2f}[/]")
    if sell_levels.get('mid_term'):
        levels_table.add_row("[green]Objetivo Medio[/]", f"[green]${sell_levels['mid_term']:.2f}[/]")
    if sell_levels.get('long_term'):
        levels_table.add_row("[green]Objetivo Largo[/]", f"[green]${sell_levels['long_term']:.2f}[/]")
    
    if res.get('buy_levels'):
        for i, level in enumerate(res['buy_levels'][:3], 1):
            levels_table.add_row(f"Nivel Compra {i}", f"[cyan]${level:.2f}[/]")
    
    console.print(levels_table)
    console.print()


def _print_alternatives(console, res):
    """Print alternative stocks (peers)."""
    if not res.get('alternatives') or not res['alternatives']:
        return
    
    console.print("[bold cyan]🔄 ALTERNATIVAS DEL SECTOR[/]")
    
    alts = res['alternatives'][:5]
    alt_list = ", ".join([f"[cyan]{alt}[/]" for alt in alts])
    console.print(f"{alt_list}")
    console.print()
