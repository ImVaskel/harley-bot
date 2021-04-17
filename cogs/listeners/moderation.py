import discord
from discord.ext import commands
from discord.utils import get
from utils.enums import LoggingEnum
from utils.subclasses import CustomEmbed
from discord import AuditLogAction
from contextlib import suppress
from datetime import date, datetime
from utils.utils import get_audit

class ModerationListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):

        if not guild.me.guild_permissions.view_audit_log:
            return

        if not LoggingEnum.NONE in (options := self.bot.utils.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get('logid')) is not None:
        
            if not LoggingEnum.MODERATION in options:
                return

            channel = self.bot.get_channel(id)

            if channel is None:
                return
            
            entry = await get_audit(guild, AuditLogAction.ban)

            embed = CustomEmbed(
                title="**Member Banned**",
                description = (
                    f"User: {user} [{user.id}]\n"
                    f"Moderator: {entry.user}"
                    f"Reason: {getattr(entry, 'reason', 'None')}\n" 
                ), timestamp=datetime.utcnow()
            ).set_thumbnail(url=user.avatar_url)

            embed.set_author(
                name=entry.user.name, url=entry.user_avatar_url
            )
            
            with suppress(discord.Forbidden):
                await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):

        if not guild.me.guild_permissions.view_audit_log:
            return

        if not LoggingEnum.NONE in (options := self.bot.utils.get_enum(guild.id)) and (id := self.bot.cache[guild.id].get('logid')) is not None:
        
            if not LoggingEnum.MODERATION in options:
                return
            
            action = None
            no_perms = False

            channel = self.bot.get_channel(id)

            if channel is None:
                return
            
            action = await get_audit(guild, AuditLogAction.unban)

            embed = CustomEmbed(
                title="**Member Unbanned**",
                description = (
                    f"User: {user} [{user.id}]\n"
                    f"Reason: {getattr(action, 'reason', 'None')}\n" 
                ), timestamp=datetime.utcnow()
            ).set_thumbnail(url=user.avatar_url)

            if action:
                embed.description += f"Moderator: {action.user}"
            
            embed.set_author(
                name=action.user.name, url=action.user.avatar_url
            )
            
            with suppress(discord.Forbidden):
                await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        if not member.guild.me.guild_permissions.view_audit_log:
            return

        if not LoggingEnum.NONE in (options := self.bot.utils.get_enum(member.guild.id)) and (id := self.bot.cache[member.guild.id].get('logid')) is not None:

            if not LoggingEnum.MODERATION in options:
                return
            
            channel = self.bot.get_channel(id)

            if channel is None:
                return
            
            entry = await get_audit(member.guild, AuditLogAction.kick)

            if entry is None:
                return

            embed = CustomEmbed(
                title="**Member Kicked**",
                description = (
                    f"User: {member} [{member.id}]\n"
                    f"Moderator: {entry.user} [{entry.user.id}]"
                    f"Reason: {getattr(entry, 'reason', 'None')}\n" 
                ), timestamp=datetime.utcnow()
            ).set_thumbnail(url=member.avatar_url)

            embed.set_author(
                name=entry.user.name, url=entry.user.avatar_url
            )

            with suppress(discord.Forbidden):
                await channel.send(embed = embed)

def setup(bot):
    bot.add_cog(ModerationListeners(bot))
