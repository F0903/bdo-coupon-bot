import discord
import importlib.metadata as metadata

BOT_VERSION = metadata.version("bdo-coupon-bot")

def assert_correct_permissions(
    user: discord.Member, channel: discord.abc.GuildChannel
) -> bool:
    perms = channel.permissions_for(user)
    return perms.send_messages
