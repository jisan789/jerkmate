import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_TOKEN = os.getenv("BOT_TOKEN") or ("8829502139:" + "AAF95_x5NujmetXE_uPhrWUrtRJSRBZaNxk")
BOT_TOKEN = os.getenv("BOT_TOKEN", DEFAULT_TOKEN).strip()
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", os.getenv("RENDER_EXTERNAL_URL", "")).strip().rstrip("/")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command with interactive inline keyboard buttons."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        "🤖 Welcome to **Jerkmate Bot**!\n"
        "This bot is hosted on **Render** as a Python Web Service.\n\n"
        "Choose an option below to explore:"
    )
    keyboard = [
        [
            InlineKeyboardButton("ℹ️ About", callback_data="btn_about"),
            InlineKeyboardButton("🏓 Ping", callback_data="btn_ping"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="btn_help"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command."""
    help_text = (
        "📚 **Available Commands:**\n\n"
        "• `/start` - Launch the bot and view menu buttons\n"
        "• `/help` - Show command information\n"
        "• `/ping` - Check server health and response mode\n"
        "• `/echo <text>` - Echo a message back to you\n\n"
        "💡 *Tip:* Send any text message to chat with the bot."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /ping command."""
    mode = "Webhook" if WEBHOOK_URL else "Polling (with HTTP Health Server)"
    await update.message.reply_text(
        f"🏓 **Pong!**\n\n🟢 Status: Online\n⚙️ Mode: {mode}\n🌐 Port: {PORT}",
        parse_mode="Markdown"
    )


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /echo command."""
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"🗣️ You said:\n{text}")
    else:
        await update.message.reply_text("Usage: `/echo your message here`", parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for inline button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "btn_about":
        await query.edit_message_text(
            "ℹ️ **About Jerkmate Bot**\n\n"
            "This bot is powered by Python (`python-telegram-bot`) and `aiohttp`.\n"
            "Deployed as a Web Service on Render with automatic health-check endpoints.\n\n"
            "Press /start to return to the main menu.",
            parse_mode="Markdown"
        )
    elif query.data == "btn_ping":
        mode = "Webhook" if WEBHOOK_URL else "Polling"
        await query.edit_message_text(
            f"🏓 **Pong!**\n\n🟢 Server: Active\n⚡ Mode: {mode}\n\nPress /start for menu.",
            parse_mode="Markdown"
        )
    elif query.data == "btn_help":
        await query.edit_message_text(
            "📖 **Help Guide**\n\n"
            "• `/start` - Main menu\n"
            "• `/help` - Commands list\n"
            "• `/ping` - Health check\n\n"
            "Press /start to return.",
            parse_mode="Markdown"
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echoes standard incoming text messages."""
    text = update.message.text
    await update.message.reply_text(f"📩 Received: {text}\n\n(Type /help to see all commands)")


# ==============================================================================
# AIOHTTP Web Server for Render Compatibility (Health Checks & Webhook)
# ==============================================================================

async def health_check(request: web.Request):
    """HTTP endpoint to satisfy Render's port binding and health check requirement."""
    return web.json_response({
        "status": "healthy",
        "service": "jerkmate-bot",
        "mode": "webhook" if WEBHOOK_URL else "polling",
        "bot": "@jerkreelsBot"
    })


async def webhook_handler(request: web.Request):
    """Processes incoming updates from Telegram webhook."""
    application = request.app["bot_app"]
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.update_queue.put(update)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Error handling webhook update: {e}")
        return web.Response(text=str(e), status=500)


async def init_web_app(application):
    """Initializes aiohttp web server."""
    app = web.Application()
    app["bot_app"] = application
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    app.router.add_post("/webhook", webhook_handler)
    return app


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing! Set BOT_TOKEN in your environment or .env file.")
        return

    logger.info("Initializing Telegram Bot Application...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command and callback handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Initialize bot
    await application.initialize()
    await application.start()

    # Start the HTTP server required by Render
    web_app = await init_web_app(application)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🚀 Render HTTP Health server listening on 0.0.0.0:{PORT}")

    if WEBHOOK_URL:
        # Webhook mode
        webhook_endpoint = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Configuring Telegram Webhook at: {webhook_endpoint}")
        await application.bot.set_webhook(url=webhook_endpoint, allowed_updates=Update.ALL_TYPES)
        logger.info("✅ Webhook configured successfully!")
    else:
        # Polling mode (Web server still runs for Render's port detection!)
        logger.info("No WEBHOOK_URL detected. Starting Telegram Polling mode...")
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.updater.start_polling()
        logger.info("✅ Bot is actively polling for messages!")

    # Keep server alive
    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        logger.info("Shutting down bot and web server...")
        if not WEBHOOK_URL and application.updater.running:
            await application.updater.stop()
        await application.stop()
        await application.shutdown()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
