#!/usr/bin/env python3
"""
Spectral Galileo - Telegram Bot
Bot de análisis financiero para Telegram con integración completa
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

# Importar módulos de Spectral Galileo
from src.spectral_galileo.core.agent import FinancialAgent
from src.spectral_galileo.core.data_manager import DataManager
from src.spectral_galileo.core import portfolio_manager, watchlist_manager
from alerts import tracker
from alerts.config import load_config

# Cargar variables de entorno
load_dotenv()

# Configuración
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
AUTHORIZED_USERS = os.getenv('AUTHORIZED_USERS', '').split(',')
MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '10'))
MAX_REQUESTS_PER_HOUR = int(os.getenv('MAX_REQUESTS_PER_HOUR', '50'))

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/telegram_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting storage
user_requests: Dict[str, List[datetime]] = defaultdict(list)


# ============================================================================
# DECORADORES Y UTILIDADES
# ============================================================================

def authorized_only(func):
    """Decorator para verificar autorización de usuario"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        username = user.username or "unknown"
        
        if username not in AUTHORIZED_USERS:
            logger.warning(f"Unauthorized access attempt by @{username} (ID: {user.id})")
            await update.message.reply_text(
                "🚫 No estás autorizado para usar este bot.\n"
                "Contacta al administrador para obtener acceso."
            )
            return
        
        logger.info(f"Command from authorized user @{username}: {update.message.text}")
        return await func(update, context)
    
    return wrapper


def rate_limit(func):
    """Decorator para limitar rate de requests"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        username = user.username or "unknown"
        now = datetime.now()
        
        # Limpiar requests antiguos
        user_requests[username] = [
            req_time for req_time in user_requests[username]
            if now - req_time < timedelta(hours=1)
        ]
        
        # Verificar límites
        recent_requests = [
            req_time for req_time in user_requests[username]
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
            await update.message.reply_text(
                f"⏳ Límite de requests alcanzado.\n"
                f"Máximo: {MAX_REQUESTS_PER_MINUTE} por minuto.\n"
                f"Espera un momento e intenta de nuevo."
            )
            logger.warning(f"Rate limit exceeded by @{username}")
            return
        
        if len(user_requests[username]) >= MAX_REQUESTS_PER_HOUR:
            await update.message.reply_text(
                f"⏳ Límite de requests alcanzado.\n"
                f"Máximo: {MAX_REQUESTS_PER_HOUR} por hora.\n"
                f"Intenta más tarde."
            )
            logger.warning(f"Hourly rate limit exceeded by @{username}")
            return
        
        # Registrar request
        user_requests[username].append(now)
        
        return await func(update, context)
    
    return wrapper


async def send_error_message(update: Update, error_msg: str):
    """Enviar mensaje de error formateado"""
    await update.message.reply_text(
        f"❌ **Error**\n\n{error_msg}",
        parse_mode='Markdown'
    )


# ============================================================================
# COMANDOS PRINCIPALES
# ============================================================================

@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida y menú principal"""
    user = update.effective_user
    
    welcome_msg = (
        f"👋 Hola **{user.first_name}**!\n\n"
        "🤖 **Spectral Galileo Bot**\n"
        "Tu asistente de análisis financiero\n\n"
        "📊 **Comandos Disponibles:**\n\n"
        "*Análisis:*\n"
        "`/analizar AAPL` - Analizar acción\n"
        "`/analizar AAPL -st` - Análisis corto plazo\n"
        "`/analizar AAPL -f` - Análisis completo\n\n"
        "*Portafolio:*\n"
        "`/portafolio` - Ver tu portafolio\n"
        "`/agregar AAPL 150.50` - Agregar acción\n"
        "`/eliminar AAPL` - Eliminar acción\n\n"
        "*Watchlist:*\n"
        "`/watchlist` - Ver tu watchlist\n"
        "`/watch AAPL` - Agregar a watchlist\n"
        "`/unwatch AAPL` - Quitar de watchlist\n\n"
        "*Alertas:*\n"
        "`/alertas` - Ver alertas activas\n"
        "`/alertas_status` - Estado del sistema\n\n"
        "*Utilidades:*\n"
        "`/stats` - Estadísticas de uso\n"
        "`/help` - Ver esta ayuda\n\n"
        "💡 Tip: Usa los botones inline para análisis rápido"
    )
    
    # Teclado inline con acciones rápidas
    keyboard = [
        [
            InlineKeyboardButton("📊 Mi Portafolio", callback_data='portfolio'),
            InlineKeyboardButton("👀 Mi Watchlist", callback_data='watchlist')
        ],
        [
            InlineKeyboardButton("🔔 Alertas", callback_data='alerts'),
            InlineKeyboardButton("📈 Estadísticas", callback_data='stats')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"User @{user.username} started the bot")


@authorized_only
@rate_limit
async def analizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /analizar - Analizar una acción"""
    if not context.args:
        await update.message.reply_text(
            "📌 **Uso correcto:**\n\n"
            "`/analizar AAPL` - Análisis básico\n"
            "`/analizar AAPL -st` - Corto plazo\n"
            "`/analizar AAPL -f` - Análisis completo",
            parse_mode='Markdown'
        )
        return
    
    ticker = context.args[0].upper()
    is_short_term = '-st' in context.args
    full_analysis = '-f' in context.args
    
    mode_text = "corto plazo" if is_short_term else "largo plazo"
    detail_text = "completo" if full_analysis else "básico"
    
    # Mensaje de progreso
    progress_msg = await update.message.reply_text(
        f"🔍 Analizando **{ticker}**...\n"
        f"Modo: {mode_text} ({detail_text})",
        parse_mode='Markdown'
    )
    
    try:
        # Ejecutar análisis
        agent = FinancialAgent(ticker, is_short_term=is_short_term)
        result = agent.run_analysis()
        
        # Extraer datos clave
        precio = result['current_price']
        veredicto = result['strategy']['verdict']
        confianza = result['strategy']['confidence']
        stop_loss = result['strategy'].get('stop_loss', 0)
        take_profit = result['strategy'].get('take_profit', 0)
        
        # Determinar emoji de veredicto
        if "FUERTE COMPRA" in veredicto:
            emoji = "🚀"
        elif "COMPRA" in veredicto:
            emoji = "🟢"
        elif "VENTA" in veredicto:
            emoji = "🔴"
        else:
            emoji = "⚪"
        
        # Mensaje de respuesta
        response = (
            f"{emoji} **{ticker}** - ${precio:.2f}\n\n"
            f"**Veredicto:** {veredicto}\n"
            f"**Confianza:** {confianza:.0f}%\n"
            f"**Stop Loss:** ${stop_loss:.2f}\n"
            f"**Take Profit:** ${take_profit:.2f}\n\n"
        )
        
        # Agregar análisis de tendencia si es NEUTRAL
        if 'NEUTRAL' in veredicto or 'MANTENER' in veredicto:
            buy_threshold = result['strategy'].get('buy_threshold')
            sell_threshold = result['strategy'].get('sell_threshold')
            
            if buy_threshold and sell_threshold:
                dist_to_buy = abs(confianza - buy_threshold)
                dist_to_sell = abs(confianza - sell_threshold)
                
                if dist_to_buy < dist_to_sell:
                    response += f"**Tendencia:** → COMPRA ({dist_to_buy:.1f} pts)\n"
                else:
                    response += f"**Tendencia:** → VENTA ({dist_to_sell:.1f} pts)\n"
        
        # Botones de acción
        keyboard = [
            [
                InlineKeyboardButton("📊 Análisis Completo", callback_data=f'full_{ticker}'),
                InlineKeyboardButton("📈 Agregar a Portfolio", callback_data=f'add_{ticker}_{precio:.2f}')
            ],
            [
                InlineKeyboardButton("👀 Watchlist", callback_data=f'watch_{ticker}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Actualizar mensaje
        await progress_msg.edit_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        logger.info(f"Analysis completed for {ticker} by @{update.effective_user.username}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error analyzing {ticker}: {error_msg}", exc_info=True)
        await progress_msg.edit_text(
            f"❌ Error al analizar **{ticker}**\n\n"
            f"Detalles: {error_msg}",
            parse_mode='Markdown'
        )


@authorized_only
@rate_limit
async def portafolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /portafolio - Ver portafolio personal"""
    progress_msg = await update.message.reply_text("📊 Cargando portafolio...")
    
    try:
        portfolio = portfolio_manager.load_portfolio()
        
        if not portfolio:
            await progress_msg.edit_text(
                "💼 **Tu Portafolio está vacío**\n\n"
                "Usa `/agregar TICKER PRECIO` para agregar acciones\n"
                "Ejemplo: `/agregar AAPL 150.50`",
                parse_mode='Markdown'
            )
            return
        
        # Agrupar por ticker
        holdings = {}
        for item in portfolio:
            ticker = item['symbol']
            if ticker not in holdings:
                holdings[ticker] = {
                    'qty': 0,
                    'avg_price': 0,
                    'total_cost': 0
                }
            holdings[ticker]['qty'] += 1
            holdings[ticker]['total_cost'] += item['buy_price']
        
        # Calcular promedios
        for ticker in holdings:
            holdings[ticker]['avg_price'] = holdings[ticker]['total_cost'] / holdings[ticker]['qty']
        
        # Obtener precios actuales
        dm = DataManager()
        response = "💼 **Tu Portafolio**\n\n"
        total_invested = 0
        total_current = 0
        
        for ticker, data in sorted(holdings.items()):
            try:
                ticker_data = dm.get_ticker_data(ticker)
                current_price = ticker_data['close'].iloc[-1]
                
                invested = data['total_cost']
                current_value = current_price * data['qty']
                pnl = ((current_value - invested) / invested) * 100
                
                total_invested += invested
                total_current += current_value
                
                pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                
                response += (
                    f"{pnl_emoji} **{ticker}**\n"
                    f"  Posiciones: {data['qty']}\n"
                    f"  Precio Prom: ${data['avg_price']:.2f}\n"
                    f"  Precio Actual: ${current_price:.2f}\n"
                    f"  P&L: {pnl:+.2f}%\n\n"
                )
            except Exception as e:
                response += f"⚠️ **{ticker}**: Error obteniendo precio\n\n"
        
        # Resumen total
        total_pnl = ((total_current - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        total_emoji = "🟢" if total_pnl > 0 else "🔴" if total_pnl < 0 else "⚪"
        
        response += (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{total_emoji} **TOTAL**\n"
            f"Invertido: ${total_invested:,.2f}\n"
            f"Valor Actual: ${total_current:,.2f}\n"
            f"P&L: {total_pnl:+.2f}%\n"
        )
        
        await progress_msg.edit_text(response, parse_mode='Markdown')
        logger.info(f"Portfolio viewed by @{update.effective_user.username}")
        
    except Exception as e:
        logger.error(f"Error loading portfolio: {str(e)}", exc_info=True)
        await progress_msg.edit_text(
            f"❌ Error al cargar portafolio\n\n{str(e)}",
            parse_mode='Markdown'
        )


@authorized_only
@rate_limit
async def watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /watchlist - Ver watchlist"""
    progress_msg = await update.message.reply_text("👀 Cargando watchlist...")
    
    try:
        tickers = watchlist_manager.get_watchlist_tickers()
        
        if not tickers:
            await progress_msg.edit_text(
                "👀 **Tu Watchlist está vacía**\n\n"
                "Usa `/watch TICKER` para agregar acciones\n"
                "Ejemplo: `/watch AAPL`",
                parse_mode='Markdown'
            )
            return
        
        response = "👀 **Tu Watchlist**\n\n"
        dm = DataManager()
        
        for ticker in tickers[:10]:  # Máximo 10 para no saturar
            try:
                data = dm.get_ticker_data(ticker)
                price = data['close'].iloc[-1]
                response += f"• **{ticker}**: ${price:.2f}\n"
            except:
                response += f"• **{ticker}**: (precio no disponible)\n"
        
        if len(tickers) > 10:
            response += f"\n... y {len(tickers) - 10} más\n"
        
        response += f"\n**Total:** {len(tickers)} acciones\n"
        
        # Botón para analizar watchlist
        keyboard = [[
            InlineKeyboardButton("📊 Analizar Watchlist", callback_data='analyze_watchlist')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await progress_msg.edit_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"Watchlist viewed by @{update.effective_user.username}")
        
    except Exception as e:
        logger.error(f"Error loading watchlist: {str(e)}", exc_info=True)
        await progress_msg.edit_text(
            f"❌ Error al cargar watchlist\n\n{str(e)}",
            parse_mode='Markdown'
        )


@authorized_only
async def alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /alertas - Ver alertas activas"""
    try:
        config = load_config()
        
        if not config.get('enabled', False):
            await update.message.reply_text(
                "🔔 **Sistema de Alertas**\n\n"
                "Estado: ⚠️ Desactivado\n\n"
                "Usa el comando desde la consola:\n"
                "`python main.py --alerts start`",
                parse_mode='Markdown'
            )
            return
        
        # Leer estado de alertas usando las funciones del módulo
        pending_alerts = tracker.get_pending_alerts()
        watchlist = watchlist_manager.get_watchlist_tickers()
        
        response = (
            "🔔 **Sistema de Alertas**\n\n"
            f"Estado: ✅ Activo\n"
            f"Alertas Pendientes: {len(pending_alerts)}\n"
            f"Tickers Monitoreados: {len(watchlist)}\n\n"
        )
        
        if watchlist:
            response += "**Watchlist:**\n"
            for ticker in watchlist[:5]:
                response += f"• {ticker}\n"
            if len(watchlist) > 5:
                response += f"... y {len(watchlist) - 5} más\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info(f"Alerts viewed by @{update.effective_user.username}")
        
    except Exception as e:
        logger.error(f"Error loading alerts: {str(e)}", exc_info=True)
        await send_error_message(update, str(e))


@authorized_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estadísticas de uso"""
    user = update.effective_user
    username = user.username or "unknown"
    
    # Contar requests del usuario
    total_requests = len(user_requests.get(username, []))
    recent_requests = len([
        req for req in user_requests.get(username, [])
        if datetime.now() - req < timedelta(minutes=1)
    ])
    
    response = (
        f"📈 **Estadísticas de Uso**\n\n"
        f"Usuario: @{username}\n"
        f"Requests (última hora): {total_requests}\n"
        f"Requests (último minuto): {recent_requests}\n\n"
        f"**Límites:**\n"
        f"• Por minuto: {MAX_REQUESTS_PER_MINUTE}\n"
        f"• Por hora: {MAX_REQUESTS_PER_HOUR}\n"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')


# ============================================================================
# CALLBACK HANDLERS (BOTONES INLINE)
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botones inline"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    username = user.username or "unknown"
    
    # Verificar autorización
    if username not in AUTHORIZED_USERS:
        await query.edit_message_text("🚫 No autorizado")
        return
    
    data = query.data
    logger.info(f"Button pressed by @{username}: {data}")
    
    try:
        if data == 'portfolio':
            # Simular comando /portafolio
            await query.message.reply_text("📊 Cargando portafolio...")
            # Aquí iría la lógica del portafolio
            
        elif data == 'watchlist':
            await query.message.reply_text("👀 Cargando watchlist...")
            
        elif data == 'alerts':
            await query.message.reply_text("🔔 Cargando alertas...")
            
        elif data == 'stats':
            # Mostrar estadísticas
            await stats(update, context)
            
        elif data.startswith('add_'):
            # Agregar a portafolio
            parts = data.split('_')
            ticker = parts[1]
            price = float(parts[2])
            portfolio_manager.add_to_portfolio(ticker, price)
            await query.edit_message_text(
                f"✅ **{ticker}** agregado al portafolio\n"
                f"Precio: ${price:.2f}",
                parse_mode='Markdown'
            )
            
        elif data.startswith('watch_'):
            # Agregar a watchlist
            ticker = data.split('_')[1]
            watchlist_manager.add_to_watchlist(ticker)
            await query.edit_message_text(
                f"✅ **{ticker}** agregado a watchlist",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}", exc_info=True)
        await query.edit_message_text(f"❌ Error: {str(e)}")


# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler global de errores"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ **Error interno del bot**\n\n"
            "El error ha sido registrado. Intenta de nuevo más tarde.",
            parse_mode='Markdown'
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Iniciar el bot"""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment")
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado")
        print("Configura el archivo .env con tu token")
        sys.exit(1)
    
    if not AUTHORIZED_USERS or AUTHORIZED_USERS == ['']:
        logger.error("No authorized users configured")
        print("❌ Error: No hay usuarios autorizados configurados")
        print("Configura AUTHORIZED_USERS en .env")
        sys.exit(1)
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting Spectral Galileo Telegram Bot...")
    logger.info(f"Authorized users: {', '.join(AUTHORIZED_USERS)}")
    
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("analizar", analizar))
    app.add_handler(CommandHandler("portafolio", portafolio))
    app.add_handler(CommandHandler("watchlist", watchlist))
    app.add_handler(CommandHandler("alertas", alertas))
    app.add_handler(CommandHandler("stats", stats))
    
    # Registrar callback handlers
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Registrar error handler
    app.add_error_handler(error_handler)
    
    # Iniciar bot
    print("🤖 Spectral Galileo Bot iniciado...")
    print(f"✅ Usuarios autorizados: {', '.join(AUTHORIZED_USERS)}")
    print("📊 Bot funcionando. Presiona Ctrl+C para detener.\n")
    
    logger.info("Bot is now polling for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n👋 Bot detenido")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)
