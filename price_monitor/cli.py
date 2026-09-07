import argparse

def main():
    print("--- CLI START ---")
    parser = argparse.ArgumentParser(description="Price Monitor CLI Manager")

    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_check = subparsers.add_parser("check", help="Check product price by URL")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
