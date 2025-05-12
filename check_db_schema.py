import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Получение списка таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Таблицы в базе данных:")
for table in tables:
    table_name = table[0]
    print(f"\nТаблица: {table_name}")
    
    # Получение информации о столбцах таблицы
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("Столбцы:")
    for column in columns:
        col_id, col_name, col_type, notnull, default_val, pk = column
        print(f"  {col_name} ({col_type}), {'NOT NULL' if notnull else 'NULL'}, {'PK' if pk else ''}")

conn.close() 