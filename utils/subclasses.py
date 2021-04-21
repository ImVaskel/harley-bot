from datetime import datetime
import logging
import traceback
import collections

from random import choice
from datetime import datetime
from typing import Optional, List, Union

import asyncdagpi
import discord
from discord.enums import ActivityType
from discord.ext import commands, ipc
import json
import asyncpg
import aiohttp
import asyncio
import os

from discord import AllowedMentions, Message, Embed, File, MessageReference

from functools import cached_property

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

async def get_prefix(bot, message: discord.Message):

    cache = bot.cache.get(message.guild.id)

    if cache is None:
        cache = bot.cache.get("default")

    prefix = cache.get("prefix", bot.config['prefix'])

    if prefix is None:
        prefix = bot.config['prefix']

    return commands.when_mentioned_or(prefix)(bot, message)

mentions = discord.AllowedMentions.none()

activity = discord.Activity(type=ActivityType.listening, name="@Harley")

intent = discord.Intents.default()
intent.members = True

class HarleyBot(commands.AutoShardedBot):
    def __init__(self, **options):
        super().__init__(get_prefix,
                            intents=intent,
                            allowed_mentions = mentions,
                            activity = activity,
                            **options)

        self._logger = logging.getLogger("Harley")

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.usage = 0
        self.cache = {}
        self.blacklisted = {}
        self.start_time = datetime.utcnow()
        self.edit_mapping = CappedDict(max_size=100)

        self.config = json.load(open("config.json"))
        self.custom_emojis = json.load(open("emojis.json"))

        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=self._loop)

        self.ipc = ipc.Server(self, self.config.get("ipc_key"))
        self.load_extension("cogs.ipc")
        
        self.db = self.loop.run_until_complete(asyncpg.create_pool(
            **self.config['db']
        ))

        
        self.cache.update({
            "default": {"prefix": self.config['prefix']}
        })

        self.load_extension("utils.utils")

        self.loop.run_until_complete(self.__ainit__())

        self.load_cogs()

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or HarleyContext)

    async def __ainit__(self):
        """Async init"""
        configs = await self.db.fetch(
            "SELECT * FROM config"
        )
        
        for config in configs:
            self.cache.update(
                {config['id']: dict(config)}
            )
        
        blacklisted = await self.db.fetch("SELECT * FROM blacklist")

        self._hook = await self.utils.get_hook()

        self._dagpi = asyncdagpi.Client(self.config['dagpi'], logging=False)

        for user in blacklisted:
            self.blacklisted.update(
                {user["id"]: user["reason"]}
            )

    def template(self, record: asyncpg.Record):
        return {
            record['id']: dict(record)
        }

    async def refresh_cache_for(self, id: int):
        config = await self.db.fetchrow("SELECT * FROM config WHERE id = $1", id)
        self.cache.update(
                {config['id']: dict(config)}
        )
    
    async def on_error(self, event_method, *args, **kwargs):
        self._logger.error(f"An Error Occurred: \n {event_method}\n")
        traceback.print_exc()

    def add_cog(self, cog):
        super(HarleyBot, self).add_cog(cog)

        if (aliases := getattr(cog, "aliases", None)) is not None:
            for alias in aliases:
                self._BotBase__cogs[alias] = cog
    
    def remove_cog(self, name):

        cog = self.get_cog(name)

        super(HarleyBot, self).remove_cog(name)

        if (aliases := getattr(cog, 'aliases', None)) is not None:
            for alias in aliases:
                self._BotBase__cogs.pop(alias)

    def load_cogs(self):
        logger = logging.getLogger("cogs")

        for cog in self.config["cogs"]:
            try:
                self.load_extension(cog)
                logger.info(f"Loaded {cog}")
            except Exception as e:
                logger.error(f"{cog} failed to load: {e}")

    def run(self, token: str = None, *, bot: bool = True, reconnect: bool = True) -> None:
        return super().run(token or self.config["token"], bot=bot, reconnect=reconnect)

    async def on_ipc_ready(self):
        self._logger.info("IPC Ready.")

    @cached_property
    def session(self):
        return self._session
    
    @cached_property
    def loop(self):
        return self._loop
    
    @cached_property
    def hook(self):
        return self._hook
    
    @cached_property
    def logger(self):
        return self._logger

    @cached_property
    def dagpi(self):
        return self._dagpi
    
class HarleyContext(commands.Context):
    
    @property
    def cache(self):
        return self.bot.cache[self.guild.id]
    
    @property
    def db(self):
        return self.bot.db

    async def refresh(self):
        await self.bot.refresh_cache_for(self.guild.id)
    
    def get_role(self, id):
        return self.guild.get_role(id)
    
    def get_channel(self, id):
        return self.guild.get_channel(id)

    async def reply(self, content= None, *args, **kwargs):
        
        if self.bot.edit_mapping.get(self.message):
            msg = self.bot.edit_mapping.get(self.message)
            return await msg.edit(content=content, *args, **kwargs)

        msg = await super().reply(content=content, *args, **kwargs)

        self.bot.edit_mapping[self.message] = msg
        
        return msg

    async def send(self, *args, **kwargs):

        if self.bot.edit_mapping.get(self.message):
            msg = self.bot.edit_mapping.get(self.message)
            return await msg.edit(*args, **kwargs)

        msg = await super().send(*args, **kwargs)

        self.bot.edit_mapping[self.message] = msg
        
        return msg

    async def confirm(self, text=None, **kwargs):
        msg = None

        reactions = [
            self.bot.custom_emojis["x-mark"],
            self.bot.custom_emojis["checkmark"]
        ]

        if (embed := kwargs.pop("embed", None)) is not None:
            msg = await self.reply(embed=embed)
        elif text is not None:
            msg = await self.reply(content=text)
        else:
            raise commands.BadArgument("No embed or text provided.")

        for reaction in reactions:
            await msg.add_reaction(reaction)

        try:
            reaction, user = await self.bot.wait_for("reaction_add",
                                                     check=(
                                                         lambda r, u: r.message.id == msg.id and
                                                                      u.id == self.author.id and
                                                                      str(r) in reactions
                                                     ), timeout=30)
            return bool(reactions.index(str(reaction)))
        except asyncio.TimeoutError:
            await self.reply(embed = CustomEmbed(description="You did not react in time."))
            return False

class CustomEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = kwargs.get("color", choice([0x4ba893, 0xc46d6c]))
        self.timestamp = kwargs.get("timestamp", datetime.utcnow())

    async def reply(self, message, **kwargs):
        """Good fucking lord, why did i make this"""
        await message.reply(embed=self, **kwargs)

class CappedDict(collections.OrderedDict):
    default_max_size = 100

    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', self.default_max_size)
        super(CappedDict, self).__init__(*args, **kwargs)
        
    def __setitem__(self, key, val):
        if key not in self:
            max_size = self.max_size - 1  # so the dict is sized properly after adding a key
            self._prune_dict(max_size)
        super(CappedDict, self).__setitem__(key, val)
        
    def update(self, **kwargs):
        super(CappedDict, self).update(**kwargs)
        self._prune_dict(self.max_size)

        
    def _prune_dict(self, max_size):
        if len(self) >= max_size:
            diff = len(self) - max_size
            for k in self.keys()[:diff]:
                del self[k]