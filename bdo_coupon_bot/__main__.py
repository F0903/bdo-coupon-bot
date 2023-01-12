from pathlib import Path
from .scanner_bot import BotManager
import logging
import sys


def setup_logging():
    root_log = logging.getLogger()
    root_log.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setLevel(logging.NOTSET)
    stdout_formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    stdout_handler.setFormatter(stdout_formatter)

    root_log.addHandler(stdout_handler)


def main():
    setup_logging()
    token_path = Path("discord_token")
    if not token_path.exists():
        print("discord_token file required to start.")
        input("Press any key to exit...")
        return
    token = token_path.read_text()
    bot = BotManager(token)
    bot.run()


if __name__ == "__main__":
    main()
