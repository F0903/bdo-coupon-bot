import discord
import importlib.metadata as metadata
import datetime

LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo

BOT_VERSION = metadata.version("bdo-coupon-bot")
SCANNER_VERSION = metadata.version("bdo-coupon-scanner")


def assert_correct_permissions(
    user: discord.Member, channel: discord.abc.GuildChannel
) -> bool:
    perms = channel.permissions_for(user)
    return perms.send_messages
