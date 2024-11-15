import sqlite3

# تابعی برای نمایش اخبار از دیتابیس
def display_news():
    # اتصال به دیتابیس
    conn = sqlite3.connect("news_data.db")
    cursor = conn.cursor()

    # دریافت اخبار از دیتابیس
    cursor.execute("SELECT title, link, date_fetched FROM news ORDER BY date_fetched DESC LIMIT 5")  # جدیدترین 5 خبر را نمایش می‌دهیم
    rows = cursor.fetchall()

    if rows:
        print("Latest news:")
        for row in rows:
            title, link, date_fetched = row
            print(f"Title: {title}\nLink: {link}\nDate: {date_fetched}\n")
    else:
        print("No data found in the database.")
        
    conn.close()

# اجرای تابع نمایش اخبار
display_news()
