import sqlite3
from decimal import Decimal
import os

def create_data_base():
    data_base = sqlite3.connect('products.db')
    db_cursor  = data_base.cursor()

    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,    
    currency TEXT NOT NULL,
    current_price DECIMAL NOT NULL,
    url TEXT NOT NULL UNIQUE

    )
    """)
    db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    price DECIMAL NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
    FOREIGN KEY (key_product_id)  REFERENCES products (id) ON DELETE CASCADE
    )
    """)

    data_base.commit()
    data_base.close()



'''ЗАМЕТКА ДЛЯ СЕБЯ:
        Вощем предполагается что будет единая БД, поэтому я убираю из функции get_db_connection дефолтный параметр  <db_path="products.db">
        Вместо него я добавил с помощью библиотеки os единый путь к БД, чтобы предотвратить создание файлов при неудачном подключении
        + я удалил в всех функциях параметр <db_path> при вызове функции get_db_connection
'''



def get_db_connection():
    db_path = os.path.abspath("products.db")
    db_uri = f"file:{db_path}?mode=rw"
    try:
    # Подключение с флагом uri=True
        conn = sqlite3.connect(db_uri, detect_types=sqlite3.PARSE_DECLTYPES, uri=True)
    except sqlite3.OperationalError:
        print(f"Ошибка: Файл базы данных по пути {db_path} не найден. Новый файл создан не был.")
    
    #conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    #Registers
    sqlite3.register_adapter(Decimal, lambda d: str(d))

    #Adapters
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))

    #conn.row_factory = sqlite3.Row  Это можно добавить после решения задачи, делает ответ из базы данных словарём с ключами - названиями столбцов
 
    return conn


def add_to_db(title, currency, price, url):
    data_base = get_db_connection("products.db")
    db_cursor = data_base.cursor()

    db_cursor.execute("INSERT INTO products VALUES (NULL, ?, ?, ?, ?)", (title, currency, price, url)) #NULL для id, т.к. он генерируется
    db_cursor.execute("SELECT id FROM products WHERE title = ?", (title,))
    id = db_cursor.fetchone()[0]
    db_cursor.execute("INSERT INTO price_history (product_id, currency, price) VALUES (?, ?, ?)", (id, currency, price))

    data_base.commit()
    data_base.close()


def show_all_products():
    data_base = get_db_connection()
    db_cursor = data_base.cursor()
    db_cursor.execute("SELECT * FROM products") # Что конкретно выводим из базы данных
    products = db_cursor.fetchall()
    data_base.close()
    for product in products:
        print(f'\ntitle - "{product[1]}", price - {product[2]}{product[3]}\n\n id - {product[0]},\t URL - {product[4]}\n')
    


def show_history():
    data_base = get_db_connection()
    db_cursor = data_base.cursor()
    db_cursor.execute("SELECT * FROM price_history") # Что конкретно выводим из ИСТОРИИ
    history = db_cursor.fetchall()
    data_base.close()
    for product in history:
        print(f'\nid - {product[1]}, price - {product[2]}{product[3]}\n\n product_id - {product[0]}, checked_at - {product[4]}\n')    


def clear_products_table(id):
    data_base = sqlite3.connect()
    db_cursor = data_base.cursor()

    if id == None:
        db_cursor.execute("DELETE FROM products")
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'products';")
    else:
        db_cursor.execute("DELETE FROM products WHERE id=?", (id,))
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'products.';")

    data_base.commit()
    data_base.close()


def clear_history_table(id):
    data_base = sqlite3.connect()
    db_cursor = data_base.cursor()

    if id == None:
        db_cursor.execute("DELETE FROM price_history")
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';")
    else:
        db_cursor.execute("DELETE FROM price_history WHERE id=?", (id,))
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';")

    data_base.commit()
    data_base.close()