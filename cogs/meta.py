import platform
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from utils import Embed, HarleyContext

BASE_URL = "https://github.com/imvaskel/harley-bot"
BRANCH = "main"


class Meta(commands.Cog):
    """Module focused on information about the bot."""

    def __init__(self, bot):
        self.bot = bot
        self.aliases = ("Misc",)

    @commands.command()
    async def ping(self, ctx, **flags):
        await ctx.reply(
            embed=Embed(description=f"Pong! `{self.bot.latency*1000:.2f} ms`")
        )

    @commands.command(aliases=("info",))
    async def botinfo(self, ctx):
        delta_uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = Embed(
            title="Info about me",
            description=(
                f"I am a bot made by {self.bot.get_user(self.bot.owner_id)} in discord.py! \n"
            ),
        ).add_field(
            name="Stats",
            value=(
                f"```diff\n"
                f"+ Guilds: {len(self.bot.guilds)}\n"
                f"+ Users: {len(self.bot.users)}\n"
                f"+ Python: {platform.python_version()}\n"
                f"+ Discord.py: {discord.__version__}\n"
                f"+ Commands Used: {self.bot.usage}\n"
                f"+ Uptime: {days}d, {hours}h, {minutes}m, {seconds}s"
                "```"
            ),
        )

        await ctx.reply(embed=embed)

    @commands.command()
    async def privacy(self, ctx):
        await ctx.reply(
            embed=Embed(
                title="You can view the privacy policy here.",
                url="https://gist.github.com/ImVaskel/c4bdf888b89e29dd16257264b9f92181",
            )
        )

    @commands.command()
    async def invite(self, ctx: HarleyContext, perms: Optional[int] = None):
        """Returns an invite for the bot."""

        embed = Embed(title="Invite")

        if perms is not None:

            if len(str(perms)) > 30:
                raise commands.BadArgument(
                    "Why is the permissions value over 30 characters long?"
                )

            embed.description = f"[Your Permissions]({discord.utils.oauth_url(ctx.bot.user.id, permissions=discord.Permissions(perms))})"
            return await ctx.reply(embed=embed)

        embed.description = (
            f"[Recommended Permissions]({discord.utils.oauth_url(ctx.bot.user.id, permissions=discord.Permissions(470150358))})\n"
            f"[No Permissions]({discord.utils.oauth_url(ctx.bot.user.id, permissions=discord.Permissions(0))})\n"
            f"[Admin Permissions]({discord.utils.oauth_url(ctx.bot.user.id, permissions=discord.Permissions(8))})"
        )

        await ctx.reply(embed=embed)

    @commands.command(name="flags")
    async def _flags(self, ctx: HarleyContext):
        """Returns an explanation of how flags work."""
        embed = Embed(
            description=(
                "Flags are used via `--flag Args`\n"
                "You can see a list of the commands flag when doing `help command`"
            )
        )

        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Meta(bot))
