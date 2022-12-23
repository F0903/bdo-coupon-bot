from io import BytesIO
from pytz import timezone
import datetime
import sys
import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from ..db import DatabaseTransaction
from ..db.subscribers import Subscriber
from ..codes import scanner as scan
from .. import __about__ as app_info


class ScannerCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    def cog_load(self) -> None:
        self.run_check_for_new_coupons.start()

    def cog_unload(self) -> None:
        self.run_check_for_new_coupons.cancel()

    async def send_message_to_subs(
        self, message: str = "", *, embed: discord.Embed | None = None
    ):
        with DatabaseTransaction() as db:
            subs = db.subscribers.get_all()
            for elem in subs:
                try:
                    ch = await self.bot.fetch_channel(elem.channelID)
                    await ch.send(message, embed=embed)
                except (PermissionError, discord.errors.Forbidden):
                    # TODO: Proper logging
                    print(
                        f"Permission error! [cID{elem.channelID} -> gID{elem.guildID}]",
                        file=sys.stderr,
                    )
                    db.subscribers.remove(elem.guildID)

    @app_commands.command(name="print_codes", description="Prints previous codes.")
    async def print_codes(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with DatabaseTransaction() as db:
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
        with DatabaseTransaction() as db:
            db.subscribers.add(Subscriber(interaction.guild_id, channel.id))
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
        with DatabaseTransaction() as db:
            db.subscribers.remove(interaction.guild.id)
        await interaction.followup.send(
            content=f"{interaction.guild.name} is now unsubscribed."
        )

    async def check_for_new_coupons(
        self, save_to_db: bool = True
    ) -> discord.Embed | None:
        coupons, elapsed_s = await scan.get_new_codes(save_to_db)
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
        embed.set_footer(text=f"{elapsed_s}s | ver. {app_info.__version__}")
        return embed

    @app_commands.check(lambda x: x.user.id == x.client.application.owner.id)
    @app_commands.command(name="scan_now_broadcast", description="[PRIVATE]")
    async def scan_now_broadcast(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            embed = await self.check_for_new_coupons(True)
            if embed is None:
                await interaction.edit_original_response(
                    content="Found no new codes :("
                )
                return
            await self.send_message_to_subs(embed=embed)
            await interaction.edit_original_response(
                content="Successfully broadcast new codes."
            )
        except Exception as e:
            await interaction.edit_original_response(content=f"Error during scan: {e}")

    # TODO: Limit usage of this from non-bot-owners to few times a day.
    @app_commands.check(lambda x: x.user.guild_permissions.administrator)
    @app_commands.command(name="scan_now", description="Scan for coupons now.")
    async def scan_now(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        try:
            embed = await self.check_for_new_coupons(False)
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
