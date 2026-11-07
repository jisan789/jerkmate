import os
import logging
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ---------------------------------------------------------------------------
# Bot Configuration (Embedded directly inside code - no external env vars required)
# ---------------------------------------------------------------------------
BOT_TOKEN = "8829502139:AAF95_x5NujmetXE_uPhrWUrtRJSRBZaNxk"
PORT = int(os.environ.get("PORT", 10000))

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("jerkmate_bot")


# ---------------------------------------------------------------------------
# Telegram Bot Handlers
# ---------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command with menu buttons."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        "🤖 **Welcome to Jerkmate Bot!**\n"
        "Running on Render Web Service via Webhook.\n\n"
        "Choose an option below:"
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
    """Handles /help command."""
    help_text = (
        "📚 **Commands List:**\n\n"
        "• `/start` - Launch bot menu\n"
        "• `/help` - Show this help\n"
        "• `/ping` - Check server status\n"
        "• `/echo <text>` - Repeat your message\n\n"
        "Send any message to chat with me!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /ping command."""
    await update.message.reply_text(
        "🏓 **Pong!**\n\n🟢 Server: Active\n⚡ Mode: Webhook on Render",
        parse_mode="Markdown",
    )


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /echo command."""
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"🗣️ You said:\n{text}")
    else:
        await update.message.reply_text("Usage: `/echo your message here`", parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "btn_about":
        await query.edit_message_text(
            "ℹ️ **About Jerkmate Bot**\n\n"
            "• Powered by Python & Telegram Webhook\n"
            "• Hosted on Render Web Service\n"
            "• Auto-sleeps when inactive to save resources!\n\n"
            "Press /start to return.",
            parse_mode="Markdown",
        )
    elif query.data == "btn_ping":
        await query.edit_message_text(
            "🏓 **Pong!**\n\n🟢 Server: Active\n⚡ Mode: Webhook\n\nPress /start for menu.",
            parse_mode="Markdown",
        )
    elif query.data == "btn_help":
        await query.edit_message_text(
            "📖 **Help Guide**\n\n"
            "Use `/start` for main menu.\n"
            "Use `/help` for commands.\n"
            "Use `/ping` to test response.\n\n"
            "Press /start to return.",
            parse_mode="Markdown",
        )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles plain text messages."""
    text = update.message.text
    await update.message.reply_text(f"📩 Received: {text}\n(Type /help for options)")


# ---------------------------------------------------------------------------
# Webhook & Web Server Endpoints
# ---------------------------------------------------------------------------
async def webhook_handler(request: web.Request):
    """Receives incoming updates from Telegram Webhook."""
    application = request.app["bot_app"]
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}", exc_info=True)
        return web.Response(text="Error", status=500)


async def set_webhook_route(request: web.Request):
    """
    Convenience endpoint: Visit this URL in your browser to automatically set the webhook!
    Example: https://your-render-app.onrender.com/set_webhook
    """
    application = request.app["bot_app"]
    host = request.headers.get("X-Forwarded-Host", request.host)
    scheme = request.headers.get("X-Forwarded-Proto", "https")
    webhook_url = f"{scheme}://{host}/webhook"

    try:
        await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
        info = await application.bot.get_webhook_info()
        return web.Response(
            text=(
                f"✅ Webhook successfully configured!\n\n"
                f"URL: {webhook_url}\n"
                f"Pending updates: {info.pending_update_count}\n\n"
                f"Your bot is now live and will wake up automatically when messages arrive!"
            ),
            content_type="text/plain",
        )
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return web.Response(text=f"❌ Failed to set webhook: {e}", status=500)


async def home_route(request: web.Request):
    """Home status page & health check endpoint for Render."""
    application = request.app["bot_app"]
    webhook_info_obj = await application.bot.get_webhook_info()
    current_webhook = webhook_info_obj.url or "Not set yet"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jerkmate Bot Server</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; background: #0f172a; color: #f8fafc; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }}
            h1 {{ color: #38bdf8; margin-top: 0; }}
            .btn {{ display: inline-block; background: #0284c7; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }}
            .btn:hover {{ background: #0369a1; }}
            code {{ background: #334155; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
            .status {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 0.85em; background: #22c55e20; color: #4ade80; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🤖 Jerkmate Bot Server</h1>
            <p><span class="status">● Server Online</span></p>
            <p><strong>Bot Username:</strong> @jerkreelsBot</p>
            <p><strong>Current Webhook URL:</strong><br><code>{current_webhook}</code></p>
            <p><strong>Pending Updates:</strong> {webhook_info_obj.pending_update_count}</p>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
            <p>To connect or refresh Telegram Webhook for this Render URL, click below:</p>
            <a class="btn" href="/set_webhook">⚡ Set Webhook to this Domain</a>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


# ---------------------------------------------------------------------------
# App Initialization Lifecycle
# ---------------------------------------------------------------------------
async def on_startup(app: web.Application):
    """Initializes the Telegram bot application during aiohttp startup."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register bot handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await application.initialize()
    await application.start()
    app["bot_app"] = application
    logger.info("✅ Telegram Bot application initialized and ready for Webhooks.")


async def on_cleanup(app: web.Application):
    """Cleans up bot resources during aiohttp shutdown."""
    logger.info("Shutting down bot application...")
    bot_app = app.get("bot_app")
    if bot_app:
        await bot_app.stop()
        await bot_app.shutdown()


def build_app() -> web.Application:
    """Builds and returns the aiohttp Web Application."""
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Routes
    app.router.add_get("/", home_route)
    app.router.add_get("/set_webhook", set_webhook_route)
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_post("/", webhook_handler)  # Also accept POST to root /

    return app


if __name__ == "__main__":
    logger.info(f"🚀 Starting Render Webhook server on port {PORT}...")
    web.run_app(build_app(), host="0.0.0.0", port=PORT)
