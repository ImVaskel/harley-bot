from contextlib import suppress
from datetime import datetime

import discord
from discord import AuditLogAction
from discord.ext import commands
from discord.ext.commands import Cog
from utils.enums import LoggingEnum
from utils.subclasses import CustomEmbed
from utils.utils import get_audit


class MessagesListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_enum = bot.utils.get_enum

    @Cog.listener('on_message_delete')
    async def on_msg_delete(self, message: discord.Message):

        if message.author.bot:
            return

        guild = message.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.MESSAGE not in options or log_channel is None:
                return
            
            entry = await get_audit(message.guild, AuditLogAction.message_delete)

            embed = CustomEmbed(
                title = "Message Deleted",
                description = (
                    f"Author: {message.author} [{message.author.id}] \n"
                    f"Channel: {message.channel} [{message.channel.id}] \n"
                ), timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="**Content**",
                value=discord.utils.escape_markdown(message.content) or "None" if not message.embeds else "Message had embeds.", inline=False
            )

            if entry:
                embed.add_field(
                    name="**Moderator**",
                    value=(
                        f"Moderator: {entry.user} [{entry.user.id}]"
                    ), inline = False
                )
            
            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)
    
    @Cog.listener('on_message_edit')
    async def on_msg_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        guild = before.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            if LoggingEnum.MESSAGE not in options or log_channel is None:
                return

            embed = CustomEmbed(
                title="Message Edited", timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="Before Content",
                value = discord.utils.escape_markdown(before.content) or "Message only contained embeds.", inline=False
            )

            embed.add_field(
                name="After Content",
                value = discord.utils.escape_markdown(after.content) or "Message only contained embeds.", inline=False
            )

            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)
    
    @Cog.listener('on_bulk_message_delete')
    async def bulk_delete(self, messages: list[discord.Message]):
        guild = messages[0].guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        if LoggingEnum.NONE not in (options := self.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get("logid")) is not None:

            log_channel = guild.get_channel(id)

            entry = None

            if LoggingEnum.MESSAGE not in options or log_channel is None:
                return
            
            if guild.me.guild_permissions.view_audit_log:
                entry = (await guild.audit_logs(limit=1, action=AuditLogAction.message_bulk_delete).flatten())[0]
                if (datetime.utcnow() - entry.created_at).total_seconds() > 5:
                    entry = None
            
            embed = CustomEmbed(
                title=f"{len(messages)} Bulk Deleted", timestamp = datetime.utcnow()
            )

            if entry:
                embed.add_field(
                    name="**Moderator**",
                    value=(
                        f"Moderator: {entry.user} [{entry.user.id}]"
                    ), inline = False
                )
            
            with suppress(discord.Forbidden):
                await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(MessagesListener(bot))
