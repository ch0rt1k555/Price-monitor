import argparse
import requests
import sqlite3
from bs4 import BeautifulSoup
from decimal import Decimal
from .models import *
from .pp_tools import *
from .db_tools import *


'''
        CONCERNS:
            Что делать с Product?
            Чат жпт сказал, что базу следует создавать, только тогда, когда она действительно требуется для выполнения операции. Я не согласен.
        TODO:          
           

            

            
        Put on the back burne:
            
        
            
        IN PROGRESS:
            
            


        DONE:
            Функция add не работает на данный момент. Необходимо добавить функцию по обновлению цены уже добавленного товара (id) и 
            отдельную функцию по парсингу продукта без открытия базы данных (html);

            Удалил лишние commit из функций;

            Я там на ночь глядя решил сделать так, чтобы при добавлении товара в products, он так же добавлялся в price_history, поэтому накосячил
            в add_to_db;

            Сделать корректный вывод у show_history;

            Разобраться с sqlite.connect(), а именно detect_type
                * 2.1    -- костыли. "Конфигурация типов должна быть общей, а не разбросанной по функциям";

            PRAGMA foreign_keys = ON -- это ???     

            2.4. СХЕМУ ТАБЛИЦ НЕОБХОДИМО УЛУЧШИТЬ

            2.5. ПУТЬ К БАЗЕ МОЖЕТ ПРИВОДИТЬ К СОЗДАНИЮ ФАЙЛОВ
            
            3.4 ОШИБКИ САЙТОВ И БАЗЫ НЕ ОБРАБАТЫВАЮТСЯ НА УРОВНЕ CLI 

            4.1. В pyproject.toml не объявлены зависимости

            Разобраться с импортом функций из отдельных файлов для более удобной работы.

             4.3. Не объявлена команда запуска установленного пакета

             4.2 Отсутствует README.md    
             
             Оформить красивый вывод price_history по id товара
        
'''


  
def main():
    create_data_base()
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    #Команды
    parser_check = subparsers.add_parser("check", help="Check product price by URL")
    parser_add = subparsers.add_parser("add", help="Add url to data base")

    parser_products_list = subparsers.add_parser('products_list', help='Show all tracked products')
    parser_history_list = subparsers.add_parser('history_list', help='Show tracking history')

    parser_show_id = subparsers.add_parser('show_id', help='Show products id by his url')
    parser_show_html = subparsers.add_parser("show_html", help="Show web_page's html")

    parser_clear_history = subparsers.add_parser('clear_history', help='Clears price_history TABLE')
    parser_clear_products = subparsers.add_parser('clear_products', help='Clears products TABLE')

    parser_show_product_history = subparsers.add_parser('show_product_history', help="Shows product's history")

    #Аргументы команд
    parser_check.add_argument('id', type=int, help='Products id from data base')
    parser_show_product_history.add_argument('id', type=int, help='Products id from data base')
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

    if args.command == 'show_product_history':
        show_history_of_product(args.id)

if __name__ == "__main__":
    main()
