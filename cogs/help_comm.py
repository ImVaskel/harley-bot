from discord.ext import commands
from utils.help import CustomHelp
from utils.subclasses import HarleyBot

class HelpCommand(commands.Cog, name="Help"):
    def __init__(self, bot: HarleyBot):
        self.bot = bot
        self._original_help = bot.help_command
        bot.help_command = CustomHelp()
        bot.help_command.cog = self
    
    def cog_unload(self) -> None:
        self.bot.help_command = self._original_help

def setup(bot):
    bot.add_cog(HelpCommand(bot))
