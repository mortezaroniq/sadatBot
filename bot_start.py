import os
import sqlite3
import requests
from telegram import Update
from deep_translator import GoogleTranslator
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time
import threading
from flask import Flask

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

# API و توکن‌ها
TELEGRAM_BOT_TOKEN = "8088475882:AAGHxr-2VZudZkunsgm3IDqaDiCucFV6L-4"
COHERE_API_KEY = "VBYG12thgKuZRaErjzWZgvz5fU3WA1Pvq2Qb3IgT"
COHERE_GENERATE_URL = "https://api.cohere.ai/v1/generate"

# تابع ذخیره چت آیدی کاربر و ارسال پیام خوش‌آمدگویی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id

    # اتصال به پایگاه داده و ذخیره چت آیدی
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (chat_id) VALUES (?)', (chat_id,))
        conn.commit()

    # ارسال پیام خوش‌آمدگویی
    await update.message.reply_text("سلام! به ربات ما خوش آمدید.")

# تابع ارسال پیام کاربر به Cohere و بازگشت پاسخ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    # Translate user message to English before sending to AI
    user_message_english = GoogleTranslator(source='fa', target='en').translate(user_message)

    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command",
        "prompt": f"(only when he asks your name, say Morteza) (the woman's name is Ruqiya) give a loving and emotional answer to the message below, imagine that the other person is your wife, (don't make the answer multi-purpose and be brief and complete) Remember that you and your wife are the people of Iran (find out what he wants and answer him and his request very well): {user_message_english}",
        "max_tokens": 150,
        "temperature": 0.5,
    }

    response = requests.post(COHERE_GENERATE_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            ai_response = response.json().get("generations")[0].get("text")
            # ترجمه پیام ارسالی به کاربر
            translated_response = GoogleTranslator(source='auto', target='fa').translate(ai_response)
            # ارسال پاسخ به کاربر
            await update.message.reply_text(translated_response)
        except (KeyError, IndexError, TypeError):
            await update.message.reply_text("متاسفانه مشکلی در پردازش پیام رخ داد.")
    else:
        await update.message.reply_text("متاسفانه اتصال به سرور با مشکل مواجه شد.")

# تابع برای اجرای فایل lovely.py هر 5 دقیقه
def run_lovely():
    while True:
        time.sleep(300)  # 5 minutes
        exec(open('lovely.py').read())

# تنظیمات ربات
def start_telegram_bot():
    # ایجاد برنامه ربات با توکن
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # اضافه کردن دستور /start به ربات
    application.add_handler(CommandHandler("start", start))

    # اضافه کردن هندلر برای پیام‌های متنی که دستور نیستند
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default port is 5000 if PORT is not set
    threading.Thread(target=run_lovely, daemon=True).start()  # Start the lovely.py execution in a separate thread
    start_telegram_bot()  # Start the Telegram bot in the main thread
    app.run(host="0.0.0.0", port=port + 1)  # Run Flask on a different port
