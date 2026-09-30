import argparse
import requests
from bs4 import BeautifulSoup



def load_html(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def show_html(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')    
    print(soup)


def parse_product(url):
    html = load_html(url)
    soup = BeautifulSoup(html, 'lxml')
    books = dict()
    all_titles = soup.findAll('h3')
    all_prices = soup.findAll('p', class_="price_color")
    for title, price in zip(all_titles, all_prices):
        title = title.find('a').get('title') # Название из списка с названиями 
        price = price.text.replace('Â', '')
        books[title] = price

    return books


def main():
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    #команды
    parser_check = subparsers.add_parser("check", help="Check product price by URL")
    parser_show_html = subparsers.add_parser("show_html", help="Show web_page's html")

    #аргументы команд
    parser_check.add_argument('url',  help='Ссылка на товар')
    parser_show_html.add_argument('url',  help='Ссылка на товар')

    
    args = parser.parse_args()

 
    if args.command == 'check':
        print(f'output:\n{parse_product(args.url)}')


    if args.command == 'show_html':
       show_html(args.url)




if __name__ == "__main__":
    main()
