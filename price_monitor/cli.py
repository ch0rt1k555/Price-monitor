import argparse
import requests
import sqlite3
from bs4 import BeautifulSoup
from decimal import Decimal
from models import Product




#Функции для работы с базой данных------------------------------------------------------------------------
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
    product_id NOT NULL,
    currency TEXT NOT NULL,
    price DECIMAL NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    data_base.commit()
    data_base.close()


def add_to_db(title, currency, price, url):
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()

    # 1. Учим SQLite конвертировать Decimal в строку при ЗАПИСИ
    sqlite3.register_adapter(Decimal, lambda d: str(d))



    db_cursor.execute(f"INSERT INTO products VALUES ( ?, ?, ?, ?)", (title, currency, price, url))

    data_base.commit()
    data_base.close()


def show_all_products():
    data_base = sqlite3.connect("products.db")
    db_cursor = data_base.cursor()
    # 2. Учим SQLite конвертировать строку обратно в Decimal при ЧТЕНИИ
# (для этого при подключении нужно включить парсинг типов)
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))
    db_cursor.execute("SELECT * FROM products") # Что конкретно выводим из базы данных
    print(db_cursor.fetchall())

    data_base.commit()
    data_base.close()



#Функции для парсинга-------------------------------------------------------------------------------------
def load_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def show_html(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')    
    print(soup.prettify())


def parse_product(id):
    #ПОДКЛЮЧАЕМ 
    data_base = sqlite3.connect('products')
    db_cursor = data_base.cursor()
    db_cursor.execute("SELECT title, currency, price, url FROM products WHERE id = ?", (id,))
    title, currency, old_price, url = db_cursor.fetchall()

    #ПАРСИМ САЙТ И НАХОДИМ ЦЕНУ
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')
    price_text = soup.find("div", class_="col-sm-6 product_main").find("p", class_="price_color").text[1:]
    currency = price_text[0] 
    new_price = Decimal(price_text[1:])

    sqlite3.register_adapter(Decimal, lambda d: str(d)) # КОНВЕРТАЦИЯ Decimal в str (честно говоря походит на костыль)
    db_cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, id))
    db_cursor.execute("INSERT INTO price_history VALUES (?, ?, ?)", (id, currency, new_price))

    data_base.commit()
    data_base.close()

    print(f'id - {id}, title - {title}\n old price - {old_price}, new price' - {new_price})



def main():
    create_data_base()
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    #Команды
    parser_check = subparsers.add_parser("check", help="Check product price by URL")
    parser_show_html = subparsers.add_parser("show_html", help="Show web_page's html")
    parser_add = subparsers.add_parser("add", help="Add url to data base")
    parser_list = subparsers.add_parser('list', help='Show all tracked products')

    #Аргументы команд
    parser_check.add_argument('id',  help='Products id from data base')
    parser_show_html.add_argument('url',  help="Product's url")
    parser_add.add_argument('url', help="Product's url")

    
    args = parser.parse_args()


    #Команды для парсинга
    if args.command == 'check':
        parse_product(args.id)


    if args.command == 'show_html':
       show_html(args.url)


    #Команды для работы с базой данных
    if args.command == 'add':
        url = args.url
        html = load_html(url)
        title, currency, price = parse_product(html)
        
        add_to_db(title, currency, price, url)

    if args.command == 'list':
        show_all_products()



if __name__ == "__main__":
    main()
