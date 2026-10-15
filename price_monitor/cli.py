import argparse
import requests
import sqlite3
from bs4 import BeautifulSoup
from decimal import Decimal
import db_tools
import pp_tools

'''
        CONCERNS:
            Что делать с Product?
            Чат жпт сказал, что базу следует создавать, только тогда, когда она действительно требуется для выполнения операции. Я не согласен.
        TODO:
            PRAGMA foreign_keys = ON -- это ???
            2.4. СХЕМУ ТАБЛИЦ НЕОБХОДИМО УЛУЧШИТЬ
            2.5. ПУТЬ К БАЗЕ МОЖЕТ ПРИВОДИТЬ К СОЗДАНИЮ ФАЙЛОВ
                      
            3.4 ОШИБКИ САЙТОВ И БАЗЫ НЕ ОБРАБАТЫВАЮТСЯ НА УРОВНЕ CLI

            4.1. В pyproject.toml не объявлены зависимости
            4.2 Отсутствует README.md
            4.3. Не объявлена команда запуска установленного пакета

        
        IN PROGRESS:
            Разобраться с sqlite.connect(), а именно detect_type
                * 2.1    -- костыли. "Конфигурация типов должна быть общей, а не разбросанной по функциям".
            


        DONE:
            Функция add не работает на данный момент. Необходимо добавить функцию по обновлению цены уже добавленного товара (id) и 
            отдельную функцию по парсингу продукта без открытия базы данных (html)
            Удалил лишние commit из функций;
            Я там на ночь глядя решил сделать так, чтобы при добавлении товара в products, он так же добавлялся в price_history, поэтому накосячил
            в add_to_db;
            Сделать корректный вывод у show_history;
        
'''

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
    product_id INTEGER NOT NULL,
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

    
#Функции для парсинга-------------------------------------------------------------------------------------
def show_id(url):
    data_base = sqlite3.connect('products.db')
    db_cursor = data_base.cursor()

    db_cursor.execute("SELECT id FROM products WHERE url = ?", (url,))
    print(db_cursor.fetchone())

    data_base.close()


def load_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def show_html(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')    
    print(soup.prettify())


def parse_product(soup):
    soup = BeautifulSoup(soup, 'lxml')
    # title_tag = soup.find("div", class_="col-sm-6 product_main").find("h1")
    # price_tag = soup.find("div", class_="col-sm-6 product_main").find("p", class_="price_color")
    title_tag = soup.select_one('div.product_main h1')
    price_tag = soup.select_one('div.product_main p.price_color')

    if title_tag is None or price_tag is None:
        raise ValueError("Не удалось найти название или цену")
    
    title = title_tag.get_text(strip=True)
    price_text = price_tag.get_text(strip=True)
    currency = price_text[1] 
    price = Decimal(price_text[2:].strip())

    return title, currency, price

    

def check_product(id):
    #ПОДКЛЮЧАЕМ 
    data_base = sqlite3.connect('products.db')
    db_cursor = data_base.cursor()
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8"))) # Конвертация в Decimal при ЧТЕНИИ
    db_cursor.execute("SELECT current_price, url FROM products WHERE id = ?", (id,))
    row = db_cursor.fetchone()

    if row is None:
        raise AttributeError('Товар с введённым id не был наден')
    
    old_price, url = row

    soup = load_html(url)
    title, currency, new_price = parse_product(soup)

    sqlite3.register_adapter(Decimal, lambda d: str(d)) # КОНВЕРТАЦИЯ Decimal в str ЗАПИСЬ
    db_cursor.execute("UPDATE products SET current_price = ? WHERE id = ?", (new_price, id))
    db_cursor.execute("INSERT INTO price_history (product_id, currency, price) VALUES (?, ?, ?)", (id, currency, new_price))

    data_base.commit()
    data_base.close()

    print(f'id - {id},  title - {title}\n old price - {currency}{old_price}, new price - {currency}{new_price}')


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
    parser_products_list = subparsers.add_parser('products_list', help='Show all tracked products')
    parser_history_list = subparsers.add_parser('history_list', help='Show tracking history') #ОДНОГО ПРОДУКТА ИЛИ ВСЕХ ???
    parser_show_id = subparsers.add_parser('show_id', help='Show products id by his url')
    parser_clear_history = subparsers.add_parser('clear_history', help='Clears price_history TABLE')
    parser_clear_products = subparsers.add_parser('clear_products', help='Clears products TABLE')

    #Аргументы команд
    parser_check.add_argument('id', type=int, help='Products id from data base')
    parser_clear_history.add_argument('id', nargs='?', type=int, help='Products id from data base')
    parser_clear_products.add_argument('id', nargs='?', type=int, help='Products id from data base')
    parser_show_html.add_argument('url', type=str, help="Product's url")
    parser_add.add_argument('url', type=str, help="Product's url")
    parser_show_id.add_argument('url', type=str, help="Product's url")
    
    args = parser.parse_args()


    #Команды для парсинга
    if args.command == 'check':
        check_product(args.id)


    if args.command == 'show_html':
       show_html(args.url)

    if args.command == 'show_id':
        show_id(args.url)


    #Команды для работы с базой данных
    if args.command == 'add':
        soup = load_html(args.url)
        title, currency, price = parse_product(soup)
        
        add_to_db(title, currency, price, args.url)
 

    if args.command == 'products_list':
        show_all_products()

    if args.command == 'history_list':
        show_history()

    if args.command == 'clear_history':
        clear_history_table(args.id)

    if args.command == 'clear_products':
        clear_products_table(args.id)



if __name__ == "__main__":
    main()
