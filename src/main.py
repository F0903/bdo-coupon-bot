import asyncio as asyn
from datetime import datetime, timedelta
from pathlib import Path
from db import ScannerDb
from discord_bot import DiscordBot, BotManager


async def run_bg(discord_client: DiscordBot):
    RUN_DELAY = 30
    next_run = datetime.now()
    next_run += timedelta(seconds=RUN_DELAY)
    try:
        while not discord_client.is_closed():
            now = datetime.now()
            if now < next_run:
                delay = (next_run - now).seconds
                await asyn.sleep(delay)
                continue
            await discord_client.send_message_to_subs("dr.cabej")
            next_run = now + timedelta(seconds=RUN_DELAY)
    except Exception as e:
        print(f"Encountered error in bg_task: {e}")


def main():
    token = Path("../discord_token.txt").read_text()
    bot = BotManager(token, run_bg)
    bot.run()


if __name__ == "__main__":
    main()
