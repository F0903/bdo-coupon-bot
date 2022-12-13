import sys
import discord
from discord import app_commands
from discord.ext import commands, tasks
from ..db import ScannerDb, ChannelElement
from ..codes import scanner as scan


class ChannelCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    def cog_load(self) -> None:
        self.run_check_for_new_coupons.start()

    def cog_unload(self) -> None:
        self.run_check_for_new_coupons.cancel()

    async def send_debug_msg(self, msg):
        DEBUG_CHANNEL_ID = 153896159834800129
        channel = await self.bot.fetch_channel(DEBUG_CHANNEL_ID)
        await channel.send(msg)

    @app_commands.command(
        name="subscribe",
        description="Subscribes the channel to the service.",
    )
    async def subscribe(
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
            db.channels.add(ChannelElement(interaction.guild_id, channel.id))
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
            db.channels.remove(interaction.guild.id)
        await interaction.followup.send(
            content=f"{interaction.guild.name} is now unsubscribed."
        )

    async def send_message_to_subs(
        self, message: str = "", *, embed: discord.Embed | None = None
    ):
        with ScannerDb() as db:
            channels = db.channels.get_all()
            for elem in channels:
                try:
                    ch = await self.bot.fetch_channel(elem.channelID)
                    await ch.send(message, embed=embed)
                except (PermissionError, discord.errors.Forbidden) as e:
                    # TODO: Proper logging
                    print(f"Error! {e}", file=sys.stderr)
                    db.channels.remove(elem.guildID)

    async def check_for_new_coupons(self) -> discord.Embed | None:
        coupons = await scan.get_new_codes()
        if len(coupons) < 1:
            return None
        coupons_str = ""
        for coupon in coupons:
            date_str = "- " + str(coupon.date) if coupon.date is not None else ""
            coupons_str += f"**{coupon.code}** {date_str}\n"
        embed = discord.Embed(
            color=discord.Colour(0x8C7B34), title="New Codes!", description=coupons_str
        )
        return embed

    # TODO: Restrict to whitelisted people.
    @app_commands.command(name="scan_now", description="Scan for coupons now.")
    async def scan_now(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            embed = await self.check_for_new_coupons()
            if embed is None:
                await self.send_message_to_subs("Found no new codes :(")
                return
            await self.send_message_to_subs(embed=embed)
        finally:
            await interaction.edit_original_response(
                content="Successfully executed scan."
            )

    # TODO: Fix duplicate message on startup (and maybe all background checks?)
    @tasks.loop(hours=24)
    async def run_check_for_new_coupons(self):
        embed = await self.check_for_new_coupons()
        if embed is None:
            return
        await self.send_message_to_subs(embed=embed)
