import argparse
import requests
import sqlite3
from bs4 import BeautifulSoup
from decimal import Decimal

'''
            ЗАМЕТКИ: 
            rowid - уже готовый id для каждого продукта в таблице
            Нужно будет оформить автоматическое создание истории(т.е. таблицы) для каждого продукта
            Возможно поле продукта в таблице Products следует изменять в зависимости от актуальной цены
'''


#Функции для работы с базой данных
def add_to_db(title, currency, price, url): #           НУЖНО ПРОТЕСТИРОВАТЬ
    data_base = sqlite3.connect("Products.db")
    db_cursor = data_base.cursor()

    # 1. Учим SQLite конвертировать Decimal в строку при ЗАПИСИ
    sqlite3.register_adapter(Decimal, lambda d: str(d))



    db_cursor.execute(f"INSERT INTO Products VALUES (?, ?, ?, ?)", (title, currency, price, url))

    data_base.commit()
    data_base.close()


def show_all_products():#                               НУЖНО ПРОТЕСТИРОВАТЬ С ЗАПИСЯМИ
    data_base = sqlite3.connect("Products.db")
    db_cursor = data_base.cursor()
    # 2. Учим SQLite конвертировать строку обратно в Decimal при ЧТЕНИИ
# (для этого при подключении нужно включить парсинг типов)
    sqlite3.register_converter("DECIMAL", lambda v: Decimal(v.decode("utf-8")))
    db_cursor.execute("SELECT * FROM Products") # Что конкретно выводим из базы данных
    print(db_cursor.fetchall())

    data_base.commit()
    data_base.close()



#Функции для парсинга
def get_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.url


def load_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def show_html(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')    
    print(soup.prettify())


def parse_product(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find("div", class_="col-sm-6 product_main").find("h1").text
    price = soup.find("div", class_="col-sm-6 product_main").find("p", class_="price_color").text[1:]
    currency = price[0] 
    price = Decimal(price[1:])
    return title, currency, price


def main():
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
    parser_check.add_argument('url',  help='Ссылка на товар')
    parser_show_html.add_argument('url',  help='Ссылка на товар')
    parser_add.add_argument('url', help='Ссылка на товар')

    
    args = parser.parse_args()


    #Команды для парсинга
    if args.command == 'check':
        html= load_html(args.url)
        url = get_url(args.url)
        title, currency, price = parse_product(html)
        print(f"Product: {title}\nPrice: {price} {currency}\nURL: {url}")

    if args.command == 'show_html':
       show_html(args.url)


    #Команды для работы с базой данных
    if args.command == 'add':
        url = get_url(args.url)
        html = load_html(url)
        title, currency, price = parse_product(html)
        add_to_db(title, currency, price, url)

    if args.command == 'list':
        show_all_products()



if __name__ == "__main__":
    main()
