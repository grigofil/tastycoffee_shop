import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    # Добавление столбца username в таблицу orders, если его нет
    cursor.execute("PRAGMA table_info(orders)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'username' not in column_names:
        print("Добавляем столбец 'username' в таблицу orders...")
        cursor.execute("ALTER TABLE orders ADD COLUMN username TEXT")
        conn.commit()
        print("Столбец 'username' успешно добавлен!")
    else:
        print("Столбец 'username' уже существует в таблице orders.")
    
except Exception as e:
    print(f"Произошла ошибка: {e}")
    conn.rollback()

conn.close() 