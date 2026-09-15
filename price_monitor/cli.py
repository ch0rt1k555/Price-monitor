import argparse
import requests
from bs4 import BeautifulSoup


def fetch_url(url):
    try:
        # Маскируемся под настоящий браузер (Chrome на Windows)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        response = requests.get(url, headers=headers)
        
        # Принудительно устанавливаем правильную кодировку текста
        response.encoding = 'utf-8' 
        
        return response.text
    except Exception as e:
        print(f"Ошибка при запросе: {e}")



def main():
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_check = subparsers.add_parser("check", help="Check product price by URL")

    parser_check.add_argument('url',  help='Ссылка на товар')

    
    args = parser.parse_args()

 
    if args.command == 'check':
        url = fetch_url(args.url) 
    
        if url != None:
            soup = BeautifulSoup(url, 'lxml')
            print(soup)
        else:
            print('Error: сайт дал неверное значение')
    

    if not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
