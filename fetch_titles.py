import sqlite3

def fetch_titles():
    # اتصال به دیتابیس
    conn = sqlite3.connect("news_data.db")
    cursor = conn.cursor()

    # بازیابی تیترها از جدول news
    cursor.execute("SELECT title, link FROM news")
    rows = cursor.fetchall()

    if rows:
        print("Fetched titles from database:")
        for idx, (title, link) in enumerate(rows, start=1):
            print(f"{idx}. {title} - {link}")
    else:
        print("No titles found in the database.")
    
    # بستن اتصال دیتابیس
    conn.close()
    return rows

# فراخوانی تابع برای نمایش تیترها
titles = fetch_titles()
