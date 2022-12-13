from pathlib import Path
from .discord_bot import BotManager


def main():
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
