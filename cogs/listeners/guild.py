from contextlib import suppress

import discord
from discord import AuditLogAction
from discord.ext import commands
from discord.ext.commands import Cog
from utils.enums import LoggingEnum
from utils.subclasses import CustomEmbed
from utils.utils import get_audit, title_format


class GuildEventListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_enum = bot.utils.get_enum

    @Cog.listener("on_guild_update")
    async def guild_update(self, before: discord.Guild, after: discord.Guild):

        if not after.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(after.id))
            and (id := self.bot.cache[after.id].get("logid")) is not None
        ):

            log_channel = after.get_channel(id)

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(after, AuditLogAction.guild_update)

            if entry is None:
                return

            embed = CustomEmbed(title="Guild Updated")

            embed.add_field(
                name="Basic Info", value=(f"Moderator: {entry.user} [{entry.user.id}]")
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    [f"{title_format(diff[0])}: `{diff[1]}`" for diff in entry.after]
                ),
            )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if not guild.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(guild.id))
            and (id := self.bot.cache[guild.id].get("logid")) is not None
        ):

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(guild, AuditLogAction.emoji_update)

            embed = CustomEmbed(title="Emojis Updated").add_field(
                name="Basic Info",
                value=(f"Moderator: {entry.user} [{entry.user.id}]\n"),
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    f"{title_format(diff[0])}: `{diff[1]}`" for diff in entry.after
                ),
                inline=False,
            )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        guild = role.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(guild.id))
            and (id := self.bot.cache[guild.id].get("logid")) is not None
        ):

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(guild, AuditLogAction.role_create)

            embed = CustomEmbed(title="Role Created").add_field(
                name="Basic Info",
                value=(
                    f"Moderator: {entry.user} [{entry.user.id}]\n"
                    f"Role: {role.name} [{role.id}]"
                ),
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    f"{title_format(diff[0])}: `{diff[1]}`"
                    for diff in entry.after
                    if diff[0] not in ("permissions", "permissions_new")
                ),
                inline=False,
            )

            for diff in entry.after:
                if diff[0] in ("permissions"):
                    embed.add_field(
                        name=title_format(diff[0]),
                        value=await self.bot.utils.paste(
                            (
                                f"{role.name}\n"
                                + "\n".join(
                                    f"{perm} : {value}"
                                    for perm, value in dict(diff[1]).items()
                                )
                            )
                        ),
                    )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        guild = role.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(guild.id))
            and (id := self.bot.cache[guild.id].get("logid")) is not None
        ):

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(guild, AuditLogAction.role_delete)

            embed = CustomEmbed(title="Role Deleted").add_field(
                name="Basic Info",
                value=(
                    f"Moderator: {entry.user} [{entry.user.id}]\n"
                    f"Role: {role.mention}"
                ),
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    f"{title_format(diff[0])}: `{diff[1]}`"
                    for diff in entry.before
                    if diff[0] not in ("permissions", "permissions_new")
                ),
                inline=False,
            )

            for diff in entry.before:
                if diff[0] in ("permissions"):
                    embed.add_field(
                        name=title_format(diff[0]),
                        value=await self.bot.utils.paste(
                            (
                                f"{role.name}\n"
                                + "\n".join(
                                    f"{perm} : {value}"
                                    for perm, value in dict(diff[1]).items()
                                )
                            )
                        ),
                    )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        guild = invite.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(guild.id))
            and (id := self.bot.cache[guild.id].get("logid")) is not None
        ):

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(guild, AuditLogAction.invite_create)

            embed = CustomEmbed(title="Invite Created")

            embed.add_field(
                name="Basic Info", value=(f"User: {entry.user} [{entry.user.id}]\n")
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    f"{title_format(diff[0])}: `{diff[1]}`" for diff in entry.after
                ),
                inline=False,
            )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        guild = invite.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if (
            LoggingEnum.NONE not in (options := self.get_enum(guild.id))
            and (id := self.bot.cache[guild.id].get("logid")) is not None
        ):

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.GUILD not in options or log_channel is None:
                return

            entry = await get_audit(guild, AuditLogAction.invite_delete)

            embed = CustomEmbed(title="Invite Deleted")

            embed.add_field(
                name="Basic Info",
                value=(f"Moderator: {entry.user} [{entry.user.id}]\n"),
            )

            embed.add_field(
                name="Advanced Info",
                value="\n".join(
                    f"{title_format(diff[0])}: `{diff[1]}`" for diff in entry.before
                ),
                inline=False,
            )

            embed.set_author(name=entry.user.name, icon_url=entry.user.avatar_url)

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildEventListeners(bot))
