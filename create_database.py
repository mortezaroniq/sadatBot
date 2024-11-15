import sqlite3

# اتصال به پایگاه داده یا ایجاد آن
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# ایجاد جدول کاربران
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY
    )
''')

conn.commit()
conn.close()
print("پایگاه داده ایجاد شد و جدول کاربران ساخته شد.")
