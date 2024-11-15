import requests
from deep_translator import GoogleTranslator
import random
import sqlite3
import json  # Added import for json

# API keys and Telegram information settings
COHERE_API_KEY = "VBYG12thgKuZRaErjzWZgvz5fU3WA1Pvq2Qb3IgT"  # Language model API key
TELEGRAM_BOT_TOKEN = "8088475882:AAGHxr-2VZudZkunsgm3IDqaDiCucFV6L-4"  # Telegram API key
LEXICA_URL = "https://lexica.art/api/v1/search"  # Image generation API URL
COHERE_GENERATE_URL = "https://api.cohere.ai/v1/generate"  # Language model API URL

# Function to generate a romantic poem or text
def generate_romantic_text():
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "command",
        "prompt": "Short romantic text to express interest, with confident and intimate language, a sense of love and affection, complete and beautiful phrasing, short and future-oriented text.",
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

# Function to fetch a random image from the Lexica API
def get_image_from_lexica(prompt):
    global LEXICA_URL  # Ensure LEXICA_URL is recognized in this scope
    params = {"q": prompt}
    response = requests.get(LEXICA_URL, params=params)
    
    if response.status_code == 200:
        try:
            images = response.json()["images"]
            if images:
                return random.choice(images)["src"]  # Select a random image
            else:
                print("No images found for this prompt.")
                return None
        except (KeyError, IndexError):
            print("No image found for this prompt.")
            return None
    else:
        print("Failed to fetch image from Lexica API.")
        return None

# Function to send a message and image to all users in the database
def send_romantic_message_to_all_users(image_url, text):
    # Translate the text to Persian
    translator = GoogleTranslator(source='auto', target='fa')
    text_fa = translator.translate(text)
    
    # Construct the message with HTML formatting
    message = f"<b>{text_fa}</b>"
    
    # Fetch all chat IDs from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    chat_ids = cursor.fetchall()
    conn.close()
    
    # Send the image with the text to each chat ID
    for chat_id_tuple in chat_ids:
        chat_id = chat_id_tuple[0]
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(telegram_url, data=data)
        
        if response.status_code == 200:
            print(f"Romantic text and image sent successfully to chat ID: {chat_id}!")
        else:
            print(f"Failed to send romantic message to chat ID: {chat_id}.")
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

# Main steps
romantic_text = generate_romantic_text()
if romantic_text:
    print(f"Generated Romantic Text: {romantic_text}")

    # Image request step
    image_url = get_image_from_lexica("A beautiful heart full of love")
    if image_url:
        # Sending to all users step
        send_romantic_message_to_all_users(image_url=image_url, text=romantic_text)
    else:
        print("Image generation failed.")
else:
    print("Romantic text generation failed.")
