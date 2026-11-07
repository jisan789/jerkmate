# 🤖 Jerkmate Telegram Bot (Render Webhook Service)

Zero-configuration Telegram Bot built with Python for Render Free Web Service.

- **Direct Video Delivery**: Sends reels directly as native playable Telegram videos (or albums for multiple reels) instead of links.
- **Group-Safe & Silent**: Completely mute in Telegram groups. Ignores all regular chat messages, chatter, and unrecognized input. Only responds to explicit commands.
- **No environment variables required**: Token and port logic are built right into the code.
- **Sleep & Auto-Wake**: Automatically sleeps on Render when inactive. Wakes up immediately upon receiving a Telegram message.

---

## 🎬 Commands
- `/reels` or `/reels <1-10>` - Sends video reels directly to the chat (e.g. `/reels 5`, `/reels 10`). Maximum 10 at once.
- `/start` - Launch menu with buttons to get videos.
- `/ping` - Health check.
- `/help` - Command list.

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
