import discord
from discord.ext import commands
from utils.subclasses import CustomEmbed, HarleyBot, HarleyContext
import re

QUOTE_REGEX = '"(.+?)"'


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx, arg: int):
        await ctx.reply(embed=CustomEmbed(title=arg))

    @test.error
    async def on_test_error(self, ctx: HarleyContext, error):
        if isinstance(error, commands.BadArgument):
            await ctx.reply(error.args)


def setup(bot):
    bot.add_cog(TestCog(bot))
