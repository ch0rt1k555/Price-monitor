import argparse
import requests
from bs4 import BeautifulSoup



def load_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def parse_product(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')
    name = soup.find('h3').find('a').get('title')
    price = soup.find('p', class_="price_color").text.replace('Â', '')
    #найти название
    #найти цену


    return f'name = {name}, price = {price}'
    '''
    Буду использовать уже реализованные функции для нахождения цены.
    Тут надо будет попыхтеть над тем, чтобы с помошью библиотеки BS найти по тегам цену, лучше обе цены.
    Благо тут можно посмотреть видео о папрсинге озона в одной из вкладок ютуба.
    '''



def main():
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    #команды
    parser_check = subparsers.add_parser("check", help="Check product price by URL")
    parser_fetch_url = subparsers.add_parser("fetch_url", help="Get product's URL")
    #аргументы команд
    parser_check.add_argument('url',  help='Ссылка на товар')
    parser_fetch_url.add_argument('url',  help='Ссылка на товар')
    


    
    args = parser.parse_args()

 
    if args.command == 'check':
        print(f'output:\n{parse_product(args.url)}')


    if args.command == 'fetch_url':
        html = fetch_url(args.url)
        print(html)



if __name__ == "__main__":
    main()
