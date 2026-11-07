# 🤖 Jerkmate Telegram Bot (Render Webhook Service)

Zero-configuration Telegram Bot built with Python for Render Free Web Service.

- **No environment variables required**: Token and port logic are built right into the code.
- **Sleep & Auto-Wake**: Uses pure Telegram Webhooks. When inactive, Render automatically sleeps the web service. When you send a message, Telegram's webhook wakes up the server.
- **Reels Generator**: Uses `reels.txt` to deliver up to 10 video reels at once with `/reels <number>`.

---

## 🎬 Commands
- `/reels <number>` - Get random reels from `reels.txt` (e.g. `/reels 10`, maximum 10 at once).
- `/start` - Launch menu with 1-click buttons.
- `/help` - View command instructions.
- `/ping` - Health check.

---

## 🚀 How to Deploy on Render

1. Open **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** ➔ **Web Service**.
3. Connect your repository: `https://github.com/jisan789/jerkmate`.
4. Keep settings as default:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`
5. Click **Deploy Web Service** (no need to configure any environment variables).

---

## ⚡ How to Set Webhook

Once deployed on Render, activate your webhook with either method:

### Method 1 (1-Click in Browser)
Open your browser and visit:
```text
https://YOUR-SERVICE-NAME.onrender.com/set_webhook
```

### Method 2 (Direct Telegram API Link)
Paste into browser:
```text
https://api.telegram.org/bot8829502139:AAF95_x5NujmetXE_uPhrWUrtRJSRBZaNxk/setWebhook?url=https://YOUR-SERVICE-NAME.onrender.com/webhook
```
*(Replace `YOUR-SERVICE-NAME` with your actual Render service name).*
