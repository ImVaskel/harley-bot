import discord
from discord.ext import commands
from utils.enums import LoggingEnum

class GuildListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

def setup(bot):
    bot.add_cog(GuildListeners(bot))
