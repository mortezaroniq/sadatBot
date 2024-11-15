import sqlite3
import requests
import json
from deep_translator import GoogleTranslator

# API keys and Telegram information settings
COHERE_API_KEY = "VBYG12thgKuZRaErjzWZgvz5fU3WA1Pvq2Qb3IgT"  # Language model API key
TELEGRAM_BOT_TOKEN = "8088475882:AAGHxr-2VZudZkunsgm3IDqaDiCucFV6L-4"  # Telegram API key
TELEGRAM_CHAT_ID = 1869521494  # Telegram chat ID
LEXICA_URL = "https://lexica.art/api/v1/search"  # Image generation API URL
COHERE_GENERATE_URL = "https://api.cohere.ai/v1/generate"  # Language model API URL

# Function to fetch title from the database
def fetch_title_from_db():
    conn = sqlite3.connect("news_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM news LIMIT 1")
    title_row = cursor.fetchone()
    if title_row:
        title = title_row[0]
        cursor.execute("DELETE FROM news WHERE title = ?", (title,))
        conn.commit()
    else:
        title = None
    conn.close()
    return title

# Function to generate an article and description from the title
def generate_article(title):
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command",
        "prompt": f"Write a short description based on the title below (less than 3000 characters): {title}",
        "max_tokens": 200,
        "temperature": 0.7,
    }

    response = requests.post(COHERE_GENERATE_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            return response.json().get("generations")[0].get("text")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print("Error in parsing JSON response:", e)
            return None
    else:
        print("Failed to get a valid response from Cohere API.")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        return None

# Function to generate a summary of the title using the language model
def generate_summary(title):
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command",
        "prompt": f"Write a short and relevant headline for this title: {title}",
        "max_tokens": 50,
        "temperature": 0.5,
    }

    response = requests.post(COHERE_GENERATE_URL, headers=headers, json=data)

    if response.status_code == 200:
        try:
            return response.json().get("generations")[0].get("text")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print("Error in parsing JSON response:", e)
            return None
    else:
        print("Failed to get a valid response from Cohere API.")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        return None

# Function to fetch an image from the Lexica API
def get_image_from_lexica(prompt):
    params = {"q": prompt}
    response = requests.get(LEXICA_URL, params=params)
    
    if response.status_code == 200:
        try:
            return response.json()["images"][0]["src"]
        except (KeyError, IndexError):
            print("No image found for this prompt.")
            return None
    else:
        print("Failed to fetch image from Lexica API.")
        return None

# Function to send a message and image to Telegram
def send_article_to_telegram(chat_id, image_url, caption, article):
    # Trim the caption and article to ensure they are not too long
    max_caption_length = 1024  # Maximum length for Telegram caption
    max_article_length = 4000  # Maximum length for Telegram article text

    # If the caption is too long, truncate it
    if len(caption) > max_caption_length:
        caption = caption[:max_caption_length] + "..."
    
    # If the article is too long, truncate it
    if len(article) > max_article_length:
        article = article[:max_article_length] + "..."
    
    # Translate the text to Persian
    translator = GoogleTranslator(source='auto', target='fa')
    caption_fa = translator.translate(caption)
    article_fa = translator.translate(article)
    
    # Construct the message with HTML formatting
    text = f"""
    <b>{caption_fa}</b>\n\n
    <i>{article_fa}</i>
    """
    
    # If the text is too long, truncate it
    max_text_length = 4096  # Maximum length for Telegram message text
    if len(text) > max_text_length:
        text = text[:max_text_length] + "..."
    
    # Send the image with the article
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": text,
        "parse_mode": "HTML"
    }
    
    response = requests.post(telegram_url, data=data)
    
    if response.status_code == 200:
        print("Article, image, and caption sent successfully to Telegram!")
    else:
        print("Failed to send article to Telegram.")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

# Main steps
title = fetch_title_from_db()
if title:
    # Article generation step
    article = generate_article(title)
    if article:
        print(f"Article for '{title}': {article}")

        # Title summarization step
        summarized_title = generate_summary(title)
        if summarized_title:
            print(f"Summarized Title for '{title}': {summarized_title}")

            # Image request step
            image_url = get_image_from_lexica(summarized_title)
            if image_url:
                # Sending to Telegram step
                send_article_to_telegram(chat_id=TELEGRAM_CHAT_ID, image_url=image_url, caption=summarized_title, article=article)
            else:
                print("Image generation failed.")
        else:
            print("Summary generation failed.")
    else:
        print("Article generation failed.")
else:
    print("No titles found in the database.")
