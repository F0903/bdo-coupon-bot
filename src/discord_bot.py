import asyncio
from typing import Any, Coroutine
import discord
from discord.ext import commands
from discord import app_commands
from db import ScannerDb


class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="set_channel",
        description="Subscribes the channel to the service.",
    )
    async def set_channel(
        self, interaction: discord.Interaction, channel: discord.abc.GuildChannel
    ):
        if channel is None:
            await interaction.response.send_message(
                "You need to pass a channel as argument!", ephemeral=True
            )
            return
        await interaction.response.defer()
        # TODO: check access to channel before adding
        with ScannerDb() as db:
            db.channels().add(interaction.guild_id, channel.id)
        await interaction.followup.send(content=f"{channel.name} is now subscribed!")

    @app_commands.command(
        name="unsub",
        description="Unsubscribes the guild from the service.",
    )
    async def unsub(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        with ScannerDb() as db:
            db.channels().remove(interaction.guild.id)
        await interaction.followup.send(
            content=f"{interaction.guild.name} is now unsubscribed."
        )


class DiscordBot(commands.Bot):
    def setup_bg_task(self, bg_task):
        self.bg_task = bg_task

    async def setup_hook(self):
        self.running_bg_task = self.loop.create_task(self.bg_task(self))

    async def setup_commands(self):
        await self.add_cog(MainCog(self))
        DEBUG_GUILD_ID = 153896159834800129
        self.tree.copy_global_to(guild=discord.Object(id=DEBUG_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=DEBUG_GUILD_ID))

    async def on_ready(self):
        print(f"Logged on discord as {self.user}")
        await self.setup_commands()

    async def send_message_to_subs(self, message: str):
        with ScannerDb() as db:
            channels = db.channels().get_all()
        for id in channels:
            # TODO: if missing access remove from db
            ch = await self.fetch_channel(id)
            await ch.send(message)


class BotManager:
    async def setup_bot(self, token: str, bg_task: Coroutine):
        self.token = token
        self.bg_task = bg_task
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = DiscordBot("", intents=intents)
        self.bot.setup_bg_task(bg_task)

    def __init__(self, token: str, bg_task: Coroutine):
        asyncio.run(self.setup_bot(token, bg_task))

    def run(self):
        self.bot.run(self.token)
