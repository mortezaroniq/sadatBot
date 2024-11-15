import sqlite3
import requests
from telegram import Update
from deep_translator import GoogleTranslator
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
        "prompt": f"(Only when he asks your name, say Morteza) (the name of the illusion wife is Ruqiya) Give a loving and emotional answer to the message below, imagine that the other party is your wife: {user_message_english}",
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

# تنظیمات ربات
def main():
    # ایجاد برنامه ربات با توکن
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # اضافه کردن دستور /start به ربات
    application.add_handler(CommandHandler("start", start))

    # اضافه کردن هندلر برای پیام‌های متنی که دستور نیستند
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرای ربات
    application.run_polling()

if __name__ == '__main__':
    main()
