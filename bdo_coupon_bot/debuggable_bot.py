from discord.ext import commands


class DebuggableBot(commands.Bot):
    async def setup_commands(self):
        self.debug_channel = await self.fetch_channel(153896159834800129)
