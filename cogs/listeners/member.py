import discord
from discord.ext import commands
from utils.subclasses import CustomEmbed


class MembersListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(MembersListener(bot))
