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

    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """)

    data_base.commit()
    data_base.close()


def get_db_connection():
    db_path = os.path.abspath("products.db")
    db_uri = f"file:{db_path}?mode=rw"
    try:
    # Подключение с флагом uri=True
        conn = sqlite3.connect(db_uri, detect_types=sqlite3.PARSE_DECLTYPES |
                                            sqlite3.PARSE_COLNAMES, uri=True)
    except sqlite3.OperationalError:
        raise sqlite3.OperationalError (f"Ошибка: Файл базы данных по пути {db_path} не найден. Новый файл создан не был.")
    
    #conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    #Registers
    sqlite3.register_adapter(Decimal, lambda d: str(d))

    #Adapters
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))

    #conn.row_factory = sqlite3.Row  Это можно добавить после решения задачи, делает ответ из базы данных словарём с ключами - названиями столбцов
 
    return conn


def add_to_db(title, currency, price, url):
    data_base = get_db_connection()
    db_cursor = data_base.cursor()
    try:
        db_cursor.execute("INSERT INTO products VALUES (NULL, ?, ?, ?, ?)", (title, currency, price, url)) #NULL для id, т.к. он генерируется
        raw_id = db_cursor.lastrowid #Сырой id (не тот, что прописан в таблице)
        db_cursor.execute("SELECT id FROM products WHERE id=?", (raw_id,))
        id = db_cursor.fetchone()[0]
        db_cursor.execute("INSERT INTO price_history (product_id, currency, price) VALUES (?, ?, ?)", (id, currency, price)) 
        data_base.commit()
        
        data_base.close()

    except sqlite3.IntegrityError:
        data_base.close()
        raise sqlite3.IntegrityError ("Данный товар уже добавлен в базу данных")


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
    db_cursor.execute("SELECT * FROM price_history ORDER BY product_id") # Что конкретно выводим из ИСТОРИИ
    history = db_cursor.fetchall()
    data_base.close()
    for product in history:
        print(f'\nid - {product[0]}, price - {product[2]}{product[3]}\n\n product_id - {product[1]}, checked_at - {product[4]}\n')    


def show_id(url):
    data_base = get_db_connection()
    db_cursor = data_base.cursor()

    db_cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
    id = db_cursor.fetchone()[0]
    if id is None:
        raise LookupError("Товар с введённым URL не был найден в базе данных")

    print(f'id - {id}')
    
    data_base.close()


def clear_products_table(id):
    data_base = get_db_connection()
    db_cursor = data_base.cursor()

    if id == None:
        db_cursor.execute("DELETE FROM products")
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'products';")
    else:
        db_cursor.execute("DELETE FROM products WHERE id=?", (id,))
        db_cursor.execute("DELETE FROM price_history WHERE product_id=?", (id,))
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'products.';")

    data_base.commit()
    data_base.close()


def clear_history_table(id):
    data_base = get_db_connection()
    db_cursor = data_base.cursor()

    if id == None:
        db_cursor.execute("DELETE FROM price_history")
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';") 
    else:
        db_cursor.execute("DELETE FROM price_history WHERE product_id=?", (id,))
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';")

    data_base.commit()
    data_base.close()


def show_history_of_product(id):
    data_base = get_db_connection()
    db_cursor = data_base.cursor()

    db_cursor.execute("SELECT * FROM price_history WHERE product_id = ? ORDER BY checked_at DESC", (id,))
    product_history = db_cursor.fetchall()
 
    data_base.close()

    for line in product_history:
        print(f'price - {line[2]}{line[3]}   when checked - {line[4]} ')
