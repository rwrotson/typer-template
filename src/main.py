from cli.app import app
from utils.console import get_console
from utils.log import setup_logging


def main():
    setup_logging()
    get_console()
    app()


if __name__ == "__main__":
    main()
