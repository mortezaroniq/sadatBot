import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime

# تابعی برای دریافت اخبار از سایت
def fetch_news():
    url = 'https://techcrunch.com/category/artificial-intelligence/'

    try:
        response = requests.get(url)
        response.raise_for_status()  # بررسی خطا در درخواست
    except requests.exceptions.RequestException as e:
        print("Error fetching news:", e)
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # استخراج اخبار جدید
    articles = soup.find_all('h3', class_='loop-card__title')

    news_list = []
    for article in articles:
        title_tag = article.find('a', class_='loop-card__title-link')
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            news_list.append((title, link))

    if news_list:  # اگر خبری موجود است
        print(f"Found {len(news_list)} news articles.")
    else:
        print("No news found.")
        
    # ذخیره در دیتابیس
    save_to_database(news_list)

# تابع ذخیره داده‌ها در دیتابیس
def save_to_database(news_list):
    # اتصال به دیتابیس و ایجاد جدول اگر وجود نداشته باشد
    conn = sqlite3.connect("news_data.db")
    cursor = conn.cursor()

    # بررسی و چاپ اینکه آیا جدول موجود است یا نه
    cursor.execute('''CREATE TABLE IF NOT EXISTS news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        link TEXT NOT NULL,
                        date_fetched TEXT NOT NULL
                    )''')
    print("Database and table verified or created.")

    # اضافه کردن هر خبر به دیتابیس
    for title, link in news_list:
        print(f"Preparing to insert news: {title}")  # نمایش عنوان قبل از ذخیره
        cursor.execute("INSERT INTO news (title, link, date_fetched) VALUES (?, ?, ?)", 
                       (title, link, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print(f"Inserted news: {title}")

    conn.commit()
    print("Changes committed to the database.")

    # بررسی داده‌های موجود در دیتابیس
    cursor.execute("SELECT * FROM news")
    rows = cursor.fetchall()
    if rows:
        print(f"Data in database: {len(rows)} records found.")
    else:
        print("No data found in the database.")
        
    conn.close()
    print("Database connection closed.")


# اجرای تابع دریافت اخبار
fetch_news()
