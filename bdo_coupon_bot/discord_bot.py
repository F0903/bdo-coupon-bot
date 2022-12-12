import asyncio
import discord
from discord.ext import commands
from .commands.scanner_commands import ChannelCommands


class DiscordBot(commands.Bot):
    async def setup_commands(self):
        await self.add_cog(ChannelCommands(self))
        DEBUG_GUILD_ID = 153896159834800129
        self.tree.copy_global_to(guild=discord.Object(id=DEBUG_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=DEBUG_GUILD_ID))

    async def on_ready(self):
        await self.setup_commands()


class BotManager:
    async def setup_bot(self, token: str):
        self.token = token
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = DiscordBot("", intents=intents)  # No prefix; only slash-commands

    def __init__(self, token: str):
        asyncio.run(self.setup_bot(token))

    def run(self):
        self.bot.run(self.token)
