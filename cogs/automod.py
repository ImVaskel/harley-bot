import discord
from discord.ext import commands
from discord.ext.commands import Cog

class Automod(commands.Cog):
    """Automoderator Listeners"""
    def __init__(self, bot):
        self.bot = bot

    #@Cog.listener

def setup(bot):
    bot.add_cog(Automod(bot))
