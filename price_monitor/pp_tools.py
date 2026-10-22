import requests
import sqlite3
from bs4 import BeautifulSoup
from decimal import Decimal
from .db_tools import * 
  
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
    data_base = get_db_connection('products.db')
    db_cursor = data_base.cursor()
    db_cursor.execute("SELECT current_price, url FROM products WHERE id = ?", (id,))
    row = db_cursor.fetchone()

    if row is None:
        raise AttributeError('Товар с введённым id не был наден')
    
    old_price, url = row

    soup = load_html(url)
    title, currency, new_price = parse_product(soup)

    db_cursor.execute("UPDATE products SET current_price = ? WHERE id = ?", (new_price, id))
    db_cursor.execute("INSERT INTO price_history (product_id, currency, price) VALUES (?, ?, ?)", (id, currency, new_price))

    data_base.commit()
    data_base.close()

    print(f'id - {id},  title - {title}\n old price - {currency}{old_price}, new price - {currency}{new_price}')

