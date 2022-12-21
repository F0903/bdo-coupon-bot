from io import BytesIO
from pytz import timezone
import datetime
import sys
import discord
from discord import app_commands
from discord.ext import commands, tasks
from ..db import ScannerDb, ChannelElement
from ..codes import scanner as scan
from ..__about__ import __version__


class ScannerCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    def cog_load(self) -> None:
        self.run_check_for_new_coupons.start()

    def cog_unload(self) -> None:
        self.run_check_for_new_coupons.cancel()

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

    @app_commands.command(name="print_codes", description="Prints previous codes.")
    async def print_codes(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with ScannerDb() as db:
            coupons = db.coupons.get_all()
        coupons_str = ""
        for coupon in coupons:
            coupons_str += f"{coupon.code},{coupon.date},{coupon.origin_link}\n"
        try:
            buffer = BytesIO(bytes(coupons_str, "utf8"))
            await interaction.followup.send(file=discord.File(buffer, "coupons.csv"))
        except discord.errors.Forbidden:
            await interaction.followup.send(
                "Not permitted to send files in this channel."
            )

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

    async def check_for_new_coupons(self) -> discord.Embed | None:
        coupons, elapsed_s = await scan.get_new_codes()
        if len(coupons) < 1:
            return None
        coupons_str = ""
        for coupon in coupons:
            date_str = f"| [{coupon.date}]({coupon.origin_link})"
            coupons_str += f"**{coupon.code}** {date_str}\n"
        embed = discord.Embed(
            color=discord.Colour(0x8C7B34),
            title="New Codes!",
            description=coupons_str,
        )
        embed.set_footer(text=f"{elapsed_s}s | ver. {__version__}")
        return embed

    # TODO: Limit usage of this from non-bot-owners to few times a day.
    @commands.has_guild_permissions(administrator=True)
    @app_commands.command(name="scan_now", description="Scan for coupons now.")
    async def scan_now(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        try:
            embed = await self.check_for_new_coupons()
            if embed is None:
                await interaction.edit_original_response(
                    content="Found no new codes :("
                )
                return
            await interaction.edit_original_response(content="", embed=embed)
        except Exception as e:
            await interaction.edit_original_response(content=f"Error during scan: {e}")

    @tasks.loop(time=datetime.time(15, 0, tzinfo=timezone("Europe/Copenhagen")))
    async def run_check_for_new_coupons(self):
        embed = await self.check_for_new_coupons()
        if embed is None:
            return
        await self.send_message_to_subs(embed=embed)
