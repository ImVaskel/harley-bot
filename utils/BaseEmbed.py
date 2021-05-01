from datetime import datetime
from random import choice

import discord


class CustomEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = kwargs.get("color", choice([0x4ba893, 0xc46d6c]))
        self.timestamp = kwargs.get("timestamp", datetime.utcnow())
