import discord
from discord.ext import commands
from utils.help import CustomHelp


class HelpCommand(commands.Cog, name="Help"):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = CustomHelp()
        bot.help_command.cog = self

def setup(bot):
    bot.add_cog(HelpCommand(bot))
