from pathlib import Path
from .scanner_bot import BotManager
import logging as log
import sys


def setup_logging() -> log.Logger:
    logger = log.getLogger(f"{__name__}")
    logger.setLevel(log.INFO)

    stdout_handler = log.StreamHandler(sys.stderr)
    stdout_handler.setLevel(log.DEBUG)
    stdout_formatter = log.Formatter("[%(levelname)s] %(name)s: %(message)s")
    stdout_handler.setFormatter(stdout_formatter)

    logger.addHandler(stdout_handler)


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
