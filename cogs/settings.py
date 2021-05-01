import re

import discord
from discord.ext import commands
from discord.ext.commands.errors import RoleNotFound
from utils.CustomConverters import OptionsConverter
from utils.enums import LoggingEnum
from utils.subclasses import CustomEmbed
from utils.utils import title_format

NEWLINE = "\n"
MENTION_REGEX = "<@(!?)([0-9]*)>"
CODEBLOCK_WITH_SYNTAX = "```{}\n{}```"
CODEBLOCK = "```\n{}```"

class PrefixConverter(commands.Converter):
    async def convert(self, ctx, argument):
        
        parsed = re.search(f"<@(!?){ctx.me.id}>", argument)

        if parsed:
            raise commands.BadArgument(
                "Prefix cannot contain a reserved string."
            )

        return argument
    
class MuteRoleConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            role = await commands.RoleConverter().convert(ctx, argument)

            if role >= ctx.me.top_role:
                raise commands.BadArgument(
                    "The role cannot be above or equal to my top role in the hierarchy."
                )
            elif role >= ctx.author.top_role:
                raise commands.BadArgument(
                    "The role cannot be above or equal to your top role in the hierarchy.")
            return role
        except RoleNotFound as e:
            raise e

class Settings(commands.Cog):
    """A module that deals with the configuration of the bot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def prefix(self, ctx, prefix: PrefixConverter):
        """Sets the guilds prefix, use quotes to get spaces in the prefix. Eg: `prefix "harley "`"""
        await self.bot.db.execute(
            "UPDATE config SET prefix = $1 WHERE id = $2", prefix, ctx.guild.id
        )
        await self.bot.refresh_cache_for(ctx.guild.id)

        await ctx.reply(embed = CustomEmbed(
            description = f"Successfully set prefix to `{prefix}`"
        ))

    @commands.group(name="log")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def log_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @log_group.command(name="set")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel for logging.
        
        NOTE: The bot needs the `view audit log` permission to log. If it doesn't have this permission, it will not send logs.
        """
        if not channel.permissions_for(ctx.me).send_messages:
            raise commands.BadArgument(
                "I cannot send messages there!"
            )

        await self.bot.db.execute("UPDATE config SET logid = $2 WHERE id = $1", ctx.guild.id, channel.id)
        await self.bot.refresh_cache_for(ctx.guild.id)

        await ctx.reply(embed=CustomEmbed(
            description = f"Set log channel to {channel.mention}."
        ))

    @log_group.command(name="options")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def log_options(self, ctx, options: commands.Greedy[OptionsConverter]):
        """
        Sets up logging options. Pass options you want and don't pass the ones that you don't want
        
        NOTE: The bot needs the `view audit log` permission to log. If it doesn't have this permission, it will not send logs.
        If you want none, pass `None`
        Options:
        ```diff
        + Message - Message change logging (Editing, deleting, etc)
        + Channels - Channel change logging (Permission overrides, deletion)
        + Guild - Guild changes (Role additions, Emoji Updates, etc)
        + Member - Member updates (Nickname, role updates)
        + Moderation - Moderation Actions (Bans, Unbans, Kicks)
        ```
        """
        settings = LoggingEnum(sum(options))
    
        await self.bot.db.execute("UPDATE config SET options = $2 WHERE id = $1", ctx.guild.id, bin(settings))

        await ctx.reply(embed = CustomEmbed(
            description = (
                "Successfully updated logging options to: \n"
                "```diff\n"
                f"{NEWLINE.join([f'+ {title_format(str(option))}' for option in list(settings)])}\n"
                "```"
            )
        ))

        await self.bot.refresh_cache_for(ctx.guild.id)

    @log_group.command(name="remove")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def remove_log(self, ctx):
        """Removes the log channel"""

        await self.bot.db.execute("UPDATE config SET logid = $2 WHERE id = $1", ctx.guild.id, None)
        await self.bot.refresh_cache_for(ctx.guild.id)

        await ctx.reply(embed=CustomEmbed(
            description = "Removed log channel."
        ))
    
    @log_group.command(name="info")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def log_info(self, ctx):
        channel = ctx.guild.get_channel(ctx.cache['logid'])
        options = self.bot.utils.get_enum(ctx.guild.id)

        channel_info = f"{getattr(channel, 'mention')}" + f" [{getattr(channel, 'id')}]" if channel else ""

        embed = CustomEmbed(
            title="Logging Info",
            description=(
                f"Channel - {channel_info}\n"
                "```\n"
                f"Options: \n{NEWLINE.join([title_format(option) for option in list(options)])}\n"
                "```"
            )
        )
        await ctx.reply(embed=embed)
    
    @commands.group(name="set")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def set_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
    
    @set_group.command(name="mute")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def set_mute(self, ctx, *, role: MuteRoleConverter):
        """Sets the muted role.
        
        ``Note``: This role has the `send messages` and `add reactions` permissions taken away.
        """
        try:
            await self.bot.db.execute(
                "UPDATE config SET muteId = $2 WHERE id = $1", ctx.guild.id, role.id
            )
        except Exception as e:
            raise e
        else:
            await ctx.reply(embed = CustomEmbed(
                description = f"Successfully set the muted role to {role.mention}"
            )
            )
        
        permissions = role.permissions
        permissions.send_messages = False
        permissions.add_reactions = False

        await role.edit(permissions=permissions, reason="Done automatically.")

        await ctx.refresh()
    
    @commands.command()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def options(self, ctx):
        """Lists the guilds current settings"""

        cache = ctx.cache

        muted_role = ctx.get_role(cache['muteid'])
        log_channel = ctx.get_channel(cache['logid'])

        options = CODEBLOCK_WITH_SYNTAX.format("diff", "\n".join([f"+ {title_format(option)}" for option in list(self.bot.utils.get_enum(ctx.guild.id))]))

        embed = CustomEmbed(
            description = (
                f"Prefix: `{cache['prefix']}`\n"
                f"Muted Role: {getattr(muted_role, 'mention', 'None')}\n"
                f"Log Channel: {getattr(log_channel, 'mention', 'None')}\n"
                f"Log Options: \n {options}\n"
            )
        )

        await ctx.reply(embed=embed)
        


def setup(bot):
    bot.add_cog(Settings(bot))
