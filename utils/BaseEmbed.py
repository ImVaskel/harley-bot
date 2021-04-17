import discord
from discord.ext import commands
from random import choice
from datetime import datetime

class CustomEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = kwargs.get("color", choice([0x4ba893, 0xc46d6c]))
        self.timestamp = kwargs.get("timestamp", datetime.utcnow())

    async def reply(self, message, **kwargs):
        """Good fucking lord, why did i make this"""
        await message.reply(embed=self, **kwargs)