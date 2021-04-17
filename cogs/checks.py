import discord
from discord.ext import commands
from utils.CustomErrors import Blacklisted

class Checks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_check(self.blacklisted)

    async def blacklisted(self, ctx):
        if reason := ctx.bot.blacklisted.get(ctx.author.id) is not None:
            raise Blacklisted(f"You are blacklisted! Reason: `{reason}`")
        return True

def setup(bot):
    bot.add_cog(Checks(bot))
