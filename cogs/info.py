import discord
from discord.ext import commands, flags
from typing import Union, Optional
from utils.subclasses import CustomEmbed, HarleyContext

TIME_TEMPLATE = "%b %d, %Y %I:%M %p"
YES_NO = ["No", "Yes"]

def title_format(input: str):
    """Formats a string from `blah_blah` to `Blah Blah`"""
    return input.title().replace("_", " ").replace("-", " ")

class Info(commands.Cog):
    """Module focused on information."""
    def __init__(self, bot):
        self.bot = bot

    @flags.add_flag("--avatar", action="store_false", help="Returns an embed without the avatar")
    @commands.command(
        aliases = (
            "whois", "ui"
        ),
        cls=flags.FlagCommand
    )
    async def userinfo(self, ctx: HarleyContext, user: Optional[Union[discord.Member, discord.User]] = None, **flags):
        """
        Returns user info, input can be a user not in the guild.
        If the user's name has a space, use quotes around their name.
        """
        user = user or ctx.author

        embed = CustomEmbed(
                    title = f"Information About {user}",
                    description = (
                        f"Created At: {user.created_at.strftime(TIME_TEMPLATE)}\n"
                        f"Bot: {YES_NO[user.bot]} \n"
                        f"ID: {user.id}"
                    )
                )

        if flags.get("avatar") is not False:
            embed.set_thumbnail(url = user.avatar_url)

        if isinstance(user, discord.Member):
                
            embed.add_field(
                name="Guild Related Info:",
                value=(
                    f"Joined At: {user.joined_at.strftime(TIME_TEMPLATE)}\n"
                    f"Nickname: {user.nick or 'None'}\n"
                    f"Top Role: {user.top_role.mention}"
                )
            )

        await ctx.reply(embed = embed)
    
    @flags.add_flag("--features", action="store_true", help="Adds a field with the guild's features.")
    @flags.add_flag("--banner", action="store_true", help="Adds a thumbnail with the guilds banner instead of the icon.")
    @commands.command(cls=flags.FlagCommand, aliases = (
        "guildinfo", "gi", "si", "guild_info", "server_info"
    ))
    async def serverinfo(self, ctx: HarleyContext, **flags):
        """
        Returns info about the server.
        """
        guild = ctx.guild

        embed = CustomEmbed(
            title = guild.name,
            description = (
                f"Owner: {guild.owner} \n"
                f"Member Count: {guild.member_count} \n"
                f"Region: {title_format(str(guild.region))} \n"
            )
        ).set_thumbnail(
            url=guild.icon_url
        )

        if flags.get("banner") is True:
            embed.set_thumbnail(
                url=guild.banner_url
            )

        if flags.get("features") is True:
            embed.add_field(
                name="Features",
                value="\n".join([title_format(feature) for feature in guild.features])
            )

        await ctx.reply(embed = embed)

    @commands.command()
    async def avatar(self, ctx: HarleyContext, user: Union[discord.Member, discord.User] = None):
        """Returns the users avatar, can be a user or member."""
        user = user or ctx.author

        await ctx.reply(embed = CustomEmbed(
            title=f"{user.name}'s avatar",
            description = f"[Url]({user.avatar_url} \"Avatar Link \")"
        ).set_image(url=user.avatar_url))

    @commands.command()
    async def emoji(self, ctx: HarleyContext, emoji: discord.PartialEmoji):
        await ctx.reply(
            embed = CustomEmbed(
                title=emoji.name,
                description=(
                    f"Animated: {YES_NO[emoji.animated]} \n"
                    f"ID {emoji.id}\n"
                )
            ).set_image(url=emoji.url)
        )

def setup(bot):
    bot.add_cog(Info(bot))
