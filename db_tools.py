import sqlite3
from decimal import Decimal


def add_to_db(title, currency, price, url):
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()

    # Конвертирование Decimal в строку при ЗАПИСИ
    sqlite3.register_adapter(Decimal, lambda d: str(d))

    db_cursor.execute("INSERT INTO products VALUES (NULL, ?, ?, ?, ?)", (title, currency, price, url)) #NULL для id, т.к. он генерируется
    db_cursor.execute("SELECT id FROM products WHERE title = ?", (title,))
    id = db_cursor.fetchone()[0]
    db_cursor.execute("INSERT INTO price_history (product_id, currency, price) VALUES (?, ?, ?)", (id, currency, price))

    data_base.commit()
    data_base.close()


def show_all_products():
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()
    # Конвертирование строки обратно в Decimal при ЧТЕНИИ
# (для этого при подключении нужно включить парсинг типов)
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))
    db_cursor.execute("SELECT * FROM products") # Что конкретно выводим из базы данных
    products = db_cursor.fetchall()
    data_base.close()
    for product in products:
        print(f'\ntitle - "{product[1]}", price - {product[2]}{product[3]}\n\n id - {product[0]},\t URL - {product[4]}\n')
    


def show_history():
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()
    # Конвертирование строки обратно в Decimal при ЧТЕНИИ
# (для этого при подключении нужно включить парсинг типов)
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))
    db_cursor.execute("SELECT * FROM price_history") # Что конкретно выводим из ИСТОРИИ
    history = db_cursor.fetchall()
    data_base.close()
    for product in history:
        print(f'\nid - {product[1]}, price - {product[2]}{product[3]}\n\n product_id - {product[0]}, checked_at - {product[4]}\n')    


def clear_products_table(id):
    data_base = sqlite3.connect("products.db")
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
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()

    if id == None:
        db_cursor.execute("DELETE FROM price_history")
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';")
    else:
        db_cursor.execute("DELETE FROM price_history WHERE id=?", (id,))
        db_cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'price_history';")

    data_base.commit()
    data_base.close()

    