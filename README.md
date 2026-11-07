# 🤖 Jerkmate Telegram Bot (Render Web Service)

A production-ready Python Telegram bot configured to run as a **Web Service on [Render](https://render.com)**.

---

## 🌟 Features

- **Render Web Service Ready**: Runs a lightweight `aiohttp` web server bound to `0.0.0.0:$PORT` with `/` and `/health` health check endpoints so Render marks your service **Healthy** without timing out.
- **Dual Mode (Polling or Webhook)**:
  - **Polling Mode (Default)**: Runs polling immediately with no domain or SSL setup required.
  - **Webhook Mode (Optional)**: Automatically activates if `WEBHOOK_URL` or `RENDER_EXTERNAL_URL` is set in your environment variables.
- **Interactive Menu**: `/start` with inline keyboard buttons.
- **Commands**:
  - `/start` - Interactive greeting with inline buttons
  - `/help` - Command list
  - `/ping` - Latency and server health check
  - `/echo <text>` - Message echoing test

---

## 🚀 How to Deploy on Render

### Step 1: Push Repository to GitHub
The repository is hosted at:
[https://github.com/jisan789/jerkmate](https://github.com/jisan789/jerkmate)

### Step 2: Create a Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository `jisan789/jerkmate`.
4. Fill in the settings:
   - **Name**: `jerkmate-bot` (or any name you prefer)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`

### Step 3: Add Environment Variables
Under the **Environment Variables** section in Render, add:

| Key | Value | Description |
|---|---|---|
| `BOT_TOKEN` | `8829502139:AAF95_x5NujmetXE_uPhrWUrtRJSRBZaNxk` | Your Telegram Bot token from @BotFather |
| `PORT` | `10000` | Port for Render HTTP service |
| `WEBHOOK_URL` *(Optional)* | `https://your-app-name.onrender.com` | If set, bot will use Webhooks instead of Polling |

### Step 4: Deploy!
Click **Create Web Service**. Render will install dependencies and start `python main.py`.
Once deployed, you will see:
```
==> Docs on specifying a build command: https://render.com/docs/build-command
==> Installing dependencies with pip install -r requirements.txt
...
==> Starting service with 'python main.py'
INFO - Render HTTP Health server listening on 0.0.0.0:10000
INFO - Bot is actively polling for messages!
==> Your service is live 🎉
```

---

## 💻 Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jisan789/jerkmate.git
   cd jerkmate
   ```

2. **Create virtual environment & install requirements:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```
