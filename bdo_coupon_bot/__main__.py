from pathlib import Path
from .discord_bot import BotManager


def main():
    token = Path("discord_token.txt").read_text()
    bot = BotManager(token)
    bot.run()


if __name__ == "__main__":
    main()
