import asyncio
import discord
from discord.ext import commands
from .cogs.scanner_cog import ScannerCog
from .debuggable_bot import DebuggableBot
from .utils import DEBUG_GUILD_ID


class ScannerBot(DebuggableBot):
    async def setup_commands(self):
        await self.add_cog(ScannerCog(self))
        self.tree.copy_global_to(guild=discord.Object(id=DEBUG_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=DEBUG_GUILD_ID))
        await super().setup_commands()

    async def on_ready(self):
        await self.setup_commands()


class BotManager:
    async def setup_bot(self, token: str):
        self.token = token
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = ScannerBot("", intents=intents)  # No prefix; only slash-commands

    def __init__(self, token: str):
        asyncio.run(self.setup_bot(token))

    def run(self):
        self.bot.run(self.token, log_handler=None)
