import discord
from discord.ext import commands, ipc
from utils.subclasses import HarleyBot

class IpcRoutes(commands.Cog):
    def __init__(self, bot: HarleyBot):
        self.bot: HarleyBot = bot

    @ipc.server.route()
    async def member_count(self, data):
        return self.bot.member_count

    @ipc.server.route()
    async def member_count_for(self, data):
        return self.bot.get_guild(int(data)).member_count

def setup(bot):
    bot.add_cog(IpcRoutes(bot))
