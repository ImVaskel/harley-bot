import time
from datetime import datetime
import discord
from discord.ext import commands
import mystbin
import json
from utils.enums import LoggingEnum

class Utilities:
    def __init__(self, bot):
        self.bot = bot
        self.mystbin = mystbin.Client()

    async def hook(self, url) -> discord.Webhook:
        return discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(self.bot.session))

    async def get_hook(self) -> discord.Webhook:
        return discord.Webhook.from_url(self.bot.config['webhook'], adapter=discord.AsyncWebhookAdapter(self.bot.session))

    async def paste(self, text, syntax=None) -> str:
        url = await self.mystbin.post(text, syntax=syntax)
        return url.url
    
    def get_enum(self, id) -> LoggingEnum:
        try:
            return LoggingEnum(int(self.bot.cache[id].get('options', '0'), 2))
        except (ValueError, TypeError):
            return LoggingEnum.NONE

TIME_TEMPLATE = "%b %d, %Y %I:%M %p"
YES_NO = ["No", "Yes"]

def title_format(input : str):
    """Formats a string from `blah_blah` to `Blah Blah`"""
    return input.title().replace("_", " ").replace("-", " ")

async def get_audit(guild: discord.Guild, action: discord.AuditLogAction):
    """Gets audit logs from a given action with a limit of 1"""
    try:
        log = (await guild.audit_logs(limit=1, action=action).flatten())[0]
        if (log.created_at - datetime.utcnow()).total_seconds() > 3:
            return None
        return log
    except (discord.Forbidden, IndexError):
        return None

class Timer:
    __slots__ = ("start_time", "end_time")

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def end(self):
        self.end_time = time.perf_counter()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    @property
    def elapsed(self):
        return self.end_time - self.start_time

def setup(bot):
    bot.utils = Utilities(bot)