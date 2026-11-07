import os
import random
import asyncio
import logging
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ---------------------------------------------------------------------------
# Bot Configuration (Embedded directly inside code - no env vars needed)
# ---------------------------------------------------------------------------
BOT_TOKEN = "9092443814:AAGv6wg5CxeTVa14JDnHXehvGrqXqCxICrM"
PORT = int(os.environ.get("PORT", 10000))

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("jerkmate_bot")

# ---------------------------------------------------------------------------
# Reels Database & Cache
# ---------------------------------------------------------------------------
REELS_FILE = os.path.join(os.path.dirname(__file__), "reels.txt")


def load_reels() -> list:
    """Loads and caches unique, valid reel video URLs from reels.txt."""
    if not os.path.exists(REELS_FILE):
        logger.warning(f"Reels file '{REELS_FILE}' not found!")
        return []
    with open(REELS_FILE, "r", encoding="utf-8") as f:
        reels = [
            line.strip()
            for line in f
            if line.strip()
            and not line.startswith("#")
            and (line.strip().startswith("http://") or line.strip().startswith("https://"))
        ]
    # Keep unique URLs
    unique_reels = list(dict.fromkeys(reels))
    logger.info(f"Loaded {len(unique_reels)} unique reel videos from {REELS_FILE}")
    return unique_reels


REELS_CACHE = load_reels()


def get_single_random_reel() -> str:
    """Retrieves a single random reel from cache."""
    global REELS_CACHE
    if not REELS_CACHE:
        REELS_CACHE = load_reels()
    if not REELS_CACHE:
        return ""
    return random.choice(REELS_CACHE)


# ---------------------------------------------------------------------------
# Background Worker: Video Sender with Automatic Error Recovery
# ---------------------------------------------------------------------------
async def send_reels_worker(bot, chat_id: int, count: int):
    """
    Background worker that sends 'count' videos individually (separate videos, not in a group).
    Automatically skips broken links and retries until all requested videos are delivered.
    """
    sent = 0
    attempts = 0
    max_attempts = count * 4  # Prevent infinite loop if multiple URLs fail

    while sent < count and attempts < max_attempts:
        attempts += 1
        url = get_single_random_reel()
        if not url:
            logger.error("No reels available in cache.")
            break

        try:
            # Send upload_video chat action
            try:
                await bot.send_chat_action(chat_id=chat_id, action="upload_video")
            except Exception:
                pass

            # Send video as separate individual video
            await bot.send_video(
                chat_id=chat_id,
                video=url,
                supports_streaming=True,
            )
            sent += 1
            logger.info(f"Delivered reel {sent}/{count} to chat {chat_id}")

            # Slight delay between separate videos for smooth delivery and rate limiting
            if sent < count:
                await asyncio.sleep(0.5)

        except Exception as e:
            logger.warning(f"Failed to send reel '{url}': {e}. Retrying with another video...")
            # Remove bad URL from in-memory cache to prevent re-picking
            try:
                REELS_CACHE.remove(url)
            except ValueError:
                pass
            await asyncio.sleep(0.2)

    logger.info(f"Finished delivering {sent}/{count} reels to chat {chat_id}")


# ---------------------------------------------------------------------------
# Telegram Command Handlers (Group-safe & Silent)
# ---------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        "🤖 **Jerkmate Reels Bot**\n\n"
        "Send `/reels` or `/reels 10` to get videos directly in the chat!\n"
        "(Maximum 10 reels at once)"
    )
    keyboard = [
        [
            InlineKeyboardButton("🎬 Get 1 Reel", callback_data="reels_1"),
            InlineKeyboardButton("🎬 Get 5 Reels", callback_data="reels_5"),
        ],
        [
            InlineKeyboardButton("🎬 Get 10 Reels", callback_data="reels_10"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")


async def reels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /reels command.
    1. Un-sends (deletes) the user's message immediately.
    2. Spawns background worker to send each video separately.
    """
    message = update.effective_message
    chat_id = update.effective_chat.id

    # 1. Un-send the triggering command message
    if message:
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Could not delete message in chat {chat_id}: {e}")

    # 2. Parse requested count
    count = 1
    if context.args:
        try:
            count = int(context.args[0])
        except ValueError:
            return  # Silent on invalid syntax in groups

    count = max(1, min(count, 10))

    # 3. Offload video delivery to background worker
    asyncio.create_task(send_reels_worker(context.bot, chat_id, count))


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /ping command."""
    await update.message.reply_text("🏓 **Pong!** Bot is online and ready.", parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    await update.message.reply_text(
        "🎬 **Commands:**\n\n"
        "• `/reels <1-10>` — Delivers reels as individual videos (e.g. `/reels 5` or `/reels 10`)\n"
        "• `/ping` — Check server status",
        parse_mode="Markdown",
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("reels_"):
        count = int(query.data.split("_")[1])
        asyncio.create_task(send_reels_worker(context.bot, query.message.chat_id, count))


# ---------------------------------------------------------------------------
# Webhook & Web Server Endpoints
# ---------------------------------------------------------------------------
async def webhook_handler(request: web.Request):
    """
    Receives incoming webhook updates from Telegram.
    Instantly returns 200 OK and closes connection to Telegram,
    while processing the update asynchronously in the backend.
    """
    application = request.app.get("bot_app")
    if not application:
        return web.Response(text="OK", status=200)

    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        # Process asynchronously in backend
        asyncio.create_task(application.process_update(update))
    except Exception as e:
        logger.error(f"Error parsing webhook update: {e}")

    # Close connection immediately with 200 OK
    return web.Response(text="OK", status=200)


async def set_webhook_route(request: web.Request):
    """
    Convenience endpoint: Open this in your browser to automatically set the Telegram webhook!
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
    reels_count = len(REELS_CACHE)

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
            <p><strong>Bot Username:</strong> @JerkmatejrBot</p>
            <p><strong>Available Reel Videos:</strong> {reels_count}</p>
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

    # Register only explicit commands (stays mute to all other group messages)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reels", reels_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    await application.initialize()
    await application.start()
    app["bot_app"] = application
    logger.info("✅ Telegram Bot application initialized (Webhook mode, mute to group chat).")


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
    app.router.add_post("/", webhook_handler)

    return app


if __name__ == "__main__":
    logger.info(f"🚀 Starting Render Webhook server on port {PORT}...")
    web.run_app(build_app(), host="0.0.0.0", port=PORT)
