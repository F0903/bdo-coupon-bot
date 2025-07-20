from discord.ext import commands
from .utils import DEBUG_GUILD_ID


class DebuggableBot(commands.Bot):
    async def setup_commands(self):
        self.debug_channel = await self.fetch_channel(DEBUG_GUILD_ID)
