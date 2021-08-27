from discord.ext import commands


class BaseFlags(commands.FlagConverter, prefix="--", delimiter=" "):
    pass
