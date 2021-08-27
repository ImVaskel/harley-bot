import discord
from discord.ext import commands
from typing import Union, Optional
from utils import Embed, HarleyContext, BaseFlags

TIME_TEMPLATE = "%b %d, %Y %I:%M %p"
YES_NO = ["No", "Yes"]


def title_format(input: str):
    """Formats a string from `blah_blah` to `Blah Blah`"""
    return input.title().replace("_", " ").replace("-", " ")


class WhoIsFlags(BaseFlags):
    avatar: bool = True


class GuildInfoFlags(BaseFlags):
    features: bool = False
    banner: bool = False


class Info(commands.Cog):
    """Module focused on information."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=("whois", "ui"))
    async def userinfo(
        self,
        ctx: HarleyContext,
        user: Optional[Union[discord.Member, discord.User]] = None,
        *,
        flags: WhoIsFlags,
    ):
        """
        Returns user info, input can be a user not in the guild.
        If the user's name has a space, use quotes around their name.
        """
        user = user or ctx.author

        embed = Embed(
            title=f"Information About {user}",
            description=(
                f"Created At: {user.created_at.strftime(TIME_TEMPLATE)}\n"
                f"Bot: {YES_NO[user.bot]} \n"
                f"ID: {user.id}"
            ),
        )

        if flags.avatar is not False:
            embed.set_thumbnail(url=user.avatar)

        if isinstance(user, discord.Member):

            embed.add_field(
                name="Guild Related Info:",
                value=(
                    f"Joined At: {user.joined_at.strftime(TIME_TEMPLATE)}\n"
                    f"Nickname: {user.nick or 'None'}\n"
                    f"Top Role: {user.top_role.mention}"
                ),
            )

        await ctx.reply(embed=embed)

    @commands.command(
        aliases=("guildinfo", "gi", "si", "guild_info", "server_info"),
    )
    async def serverinfo(self, ctx: HarleyContext, *, flags: GuildInfoFlags):
        """
        Returns info about the server.
        """
        guild = ctx.guild

        embed = Embed(
            title=guild.name,
            description=(
                f"Owner: {guild.owner} \n"
                f"Member Count: {guild.member_count} \n"
                f"Region: {title_format(str(guild.region))} \n"
            ),
        ).set_thumbnail(url=guild.icon)

        if flags.banner is True:
            embed.set_thumbnail(url=guild.banner)

        if flags.features is True:
            embed.add_field(
                name="Features",
                value="\n".join([title_format(feature) for feature in guild.features]),
            )

        await ctx.reply(embed=embed)

    @commands.command()
    async def avatar(
        self, ctx: HarleyContext, user: Union[discord.Member, discord.User] = None
    ):
        """Returns the users avatar, can be a user or member."""
        user = user or ctx.author

        await ctx.reply(
            embed=Embed(
                title=f"{user.name}'s avatar",
                description=f'[Url]({user.avatar} "Avatar Link ")',
            ).set_image(url=user.avatar)
        )

    @commands.command()
    async def emoji(self, ctx: HarleyContext, emoji: discord.PartialEmoji):
        await ctx.reply(
            embed=Embed(
                title=emoji.name,
                description=(
                    f"Animated: {YES_NO[emoji.animated]} \n" f"ID {emoji.id}\n"
                ),
            ).set_image(url=emoji.url)
        )


def setup(bot):
    bot.add_cog(Info(bot))
