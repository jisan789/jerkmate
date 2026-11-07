# 🤖 Jerkmate Telegram Bot (Render Webhook Service)

Zero-configuration Telegram Bot built with Python for Render Free Web Service.

- **No environment variables required**: Token and port logic are built right into the code.
- **Sleep & Auto-Wake**: Uses pure Telegram Webhooks. When inactive, Render automatically sleeps the web service. When you send a message, Telegram's webhook wakes up the server.

---

## 🚀 How to Deploy on Render

1. Open **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** ➔ **Web Service**.
3. Connect your repository: `https://github.com/jisan789/jerkmate`.
4. Leave settings as default:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`
5. Click **Deploy Web Service** (no need to add any environment variables!).

---

## ⚡ How to Set Webhook (Single Step)

Once deployed, Render gives you a URL (for example: `https://jerkmate-xxxx.onrender.com`).

You have **two easy ways** to activate the webhook:

### Method 1 (Easiest - 1 Click)
Simply open this in your browser:
```text
https://YOUR-RENDER-NAME.onrender.com/set_webhook
```
It will automatically connect your bot to Telegram and confirm with:
`✅ Webhook successfully configured!`

---

### Method 2 (Direct Telegram API URL)
Paste this URL into your browser (replace `YOUR-RENDER-NAME` with your actual Render service name):

```text
https://api.telegram.org/bot8829502139:AAF95_x5NujmetXE_uPhrWUrtRJSRBZaNxk/setWebhook?url=https://YOUR-RENDER-NAME.onrender.com/webhook
```

---

## 💤 How Sleep & Wakeup Works on Render Free Tier
- **When no one is using the bot:** Render automatically puts the service to sleep after 15 minutes of inactivity.
- **When you message the bot:** Telegram immediately pings your webhook. Render wakes the server up from sleep. If it was sleeping, the first message triggers the wake-up; send your command (like `/start`) and the bot will reply and stay awake while you are chatting!
