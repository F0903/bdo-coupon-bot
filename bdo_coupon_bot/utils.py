import discord
import importlib.metadata as metadata
import datetime
from typing import Callable

DEBUG_GUILD_ID = 153896159834800129

LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo

BOT_VERSION = metadata.version("bdo-coupon-bot")
SCANNER_VERSION = metadata.version("bdo-coupon-scanner")


def assert_correct_permissions(
    user: discord.Member, channel: discord.abc.GuildChannel
) -> bool:
    perms = channel.permissions_for(user)
    return perms.send_messages


def assert_owner(interaction: discord.Interaction) -> bool:
    app = interaction.client.application
    if app is None:
        return False

    return interaction.user.id == app.owner.id


def assert_admin(interaction: discord.Interaction) -> bool:
    user = interaction.user

    if not isinstance(user, discord.Member):
        return False

    resolved_perms = user.resolved_permissions
    if not resolved_perms:
        return False

    return resolved_perms.administrator
