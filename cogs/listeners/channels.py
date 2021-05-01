from contextlib import suppress
from datetime import datetime

import discord
from discord import AuditLogAction
from discord.ext import commands
from discord.ext.commands import Cog
from utils.enums import LoggingEnum
from utils.subclasses import CustomEmbed
from utils.utils import get_audit, title_format

TIME_TEMPLATE = "%b %d, %Y %I:%M %p"

def format_overwrites(overwrites):
    formatted = ""
    for entry in overwrites:
        formatted += f"{entry[0].name} \n"

        for permission in list(entry[1]):
            
            formatted += f"{title_format(permission[0])} - {permission[1]}\n"

        formatted += "\n\n"
    
    return formatted

class ChannelsListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_enum = bot.utils.get_enum

    @Cog.listener('on_guild_channel_delete')
    async def on_channel_delete(self, channel):
        guild = channel.guild

        if not channel.guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.CHANNELS not in options or log_channel is None:
                return
            
            if guild.me.guild_permissions.view_audit_log:
                entry = (await guild.audit_logs(limit=1, action=AuditLogAction.channel_delete).flatten())[0]

            embed = CustomEmbed(
                title="Channel Deleted", timestamp = datetime.utcnow()
            )

            embed.add_field(
                name="**Channel**",
                value=(
                    f"Name: `{channel}` [{channel.id}]\n"
                    f"Type: `{channel.type}`\n"
                    f"Position: `{channel.position}`\n"
                    f"Created At: `{channel.created_at.strftime(TIME_TEMPLATE)}` (UTC)"
                )
            )

            if entry is not None:

                for diff in entry.after:
                    if diff[0] == 'overwrites':
                        if diff[1] is None:
                            continue
                        url = await self.bot.utils.paste(format_overwrites(diff[1]), syntax=None)
                        embed.add_field(
                            name="Overwrites", value=url or "None"
                        )
                    else:
                        embed.add_field(
                            name=title_format(diff[0]), value=f"`{diff[1]}`", inline=False
                        )

                embed.add_field(
                    name="**Moderator**",
                    value=(
                        f"{entry.user}"
                    ), inline=False
                )
            else:
                embed.add_field(
                    embed.add_field(
                        name = "**Moderator**",
                        value = "Cannot access the audit log to get more info."
                    )
                )
            
            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener('on_guild_channel_create')
    async def on_channel_create(self, channel):
        guild = channel.guild

        if not channel.guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            if LoggingEnum.CHANNELS not in options or log_channel is None:
                return
            
            entry = await get_audit(channel.guild, AuditLogAction.channel_create)

            if entry is None:
                return

            embed = CustomEmbed(
                title="Channel Created", timestamp = datetime.utcnow()
            )

            embed.add_field(
                name="**Basic Info**",
                value=(
                    f"Name: `{channel}` [{channel.id}]\n"
                    f"Type: `{channel.type}`\n"
                    f"Position: `{channel.position}`\n"
                    f"Created At: `{channel.created_at.strftime(TIME_TEMPLATE)}` (UTC)\n"
                    f"Category: `{channel.category}`"
                    f"Moderator: {entry.user} [{entry.user.id}]\n"
                )
            )

            embed.add_field(
                name="Advanced Info",
                value = "\n".join([
                    title_format(diff[0] + f"`{diff[1]}`" for diff in entry.after if diff[0] != "overwrites")
                ])
            )

            for diff in entry.after:
                if diff[0] == "overwrites":
                    embed.add_field(
                        name="Overwrites",
                        value=await self.bot.utils.paste(format_overwrites(diff[1]))
                    )
            
            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

    @Cog.listener('on_guild_channel_update')
    async def on_channel_update(self, before, after):

        guild = after.guild

        if not after.guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            if LoggingEnum.CHANNELS not in options or log_channel is None:
                return
            
            if guild.me.guild_permissions.view_audit_log:
                entry = (await guild.audit_logs(limit=1, action=AuditLogAction.channel_update).flatten())[0]
            
            embed = CustomEmbed(
                title="Channel Edited", timestamp = datetime.utcnow()
            )

            embed.add_field(
                name="Basic Info",
                value=(
                    f"Channel: {after.mention} [{after.id}] \n"
                    f"Moderator: {entry.user} [{entry.user.id}]\n"
                )
            )

            embed.add_field(
                name="Advanced Info",
                value = "\n".join([
                    title_format(diff[0] + f"`{diff[1]}`" for diff in entry.after if diff[0] != "overwrites")
                ])
            )

            for diff in entry.after:
                if diff[0] == "overwrites":
                    embed.add_field(
                        name="Overwrites",
                        value=await self.bot.utils.paste(format_overwrites(diff[1]))
                    )

            embed.set_author(
                name=entry.user.name, url=entry.user.avatar_url
            )

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)
    
    # @Cog.listener('on_guild_channel_pins_update')
    # async def pins_update(self, channel, last_pin):
    #     guild = channel.guild

    #     if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

    #         log_channel = guild.get_channel(id)

    #         entry = None
    #         url = None

    #         if not LoggingEnum.CHANNELS in options or log_channel is None:
    #             return
            
    #         if guild.me.guild_permissions.view_audit_log:
    #             entry = (await guild.audit_logs(limit=1, action=AuditLogAction.message_pin).flatten())[0]
            
    #         embed = CustomEmbed(
    #             title="Message Pinned",
    #             description=(
    #                 f"Channel:{channel.mention} [{channel.id}]\n"
    #             )
    #         )


def setup(bot):
    bot.add_cog(ChannelsListener(bot))
