import asyncio
import collections
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from random import choice
from typing import Dict, Optional

import aiohttp
import asyncdagpi
import asyncpg
import discord
from discord import Message
from discord.enums import ActivityType
from discord.ext import commands, ipc

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


async def get_prefix(bot, message: discord.Message) -> str:

    if message.guild is None:
        return "h,"

    cache = bot.cache.get(message.guild.id)

    if cache is None:
        cache = bot.cache.get("default")

    prefix = cache.get("prefix", bot.config["prefix"])

    if prefix is None:
        prefix = bot.config["prefix"]

    return commands.when_mentioned_or(prefix)(bot, message)


intent = discord.Intents.default()
intent.members = True


class HarleyBot(commands.AutoShardedBot):
    def __init__(self, **options):
        super().__init__(
            get_prefix,
            intents=intent,
            allowed_mentions=discord.AllowedMentions.none(),
            activity=discord.Activity(type=ActivityType.listening, name="@Harley"),
            **options,
        )

        self._logger = logging.getLogger("Harley")

        self._BotBase__cogs = commands.core._CaseInsensitiveDict()
        self.usage = 0
        self.cache = {}
        self.blacklisted = {}
        self.start_time = datetime.utcnow()
        self.edit_mapping: Dict[Message, Message] = CappedDict(max_size=100)

        self.config = json.load(open("config.json"))
        self.custom_emojis = json.load(open("emojis.json"))

        self._session = aiohttp.ClientSession(loop=self.loop)

        self.ipc = ipc.Server(self, self.config.get("ipc_key"))
        self.load_extension("cogs.ipc")

        self.db = self.loop.run_until_complete(asyncpg.create_pool(**self.config["db"]))

        self._dagpi = asyncdagpi.Client(self.config["dagpi"])

        self.cache.update({"default": {"prefix": self.config["prefix"]}})

        self.load_extension("utils.utils")

        self.loop.run_until_complete(self._ainit())

        self.load_cogs()

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or HarleyContext)

    async def _ainit(self):
        """Async init"""
        configs = await self.db.fetch("SELECT * FROM config")

        for config in configs:
            self.cache.update({config["id"]: dict(config)})

        blacklisted = await self.db.fetch("SELECT * FROM blacklist")

        self._hook = await self.utils.get_hook()

        for user in blacklisted:
            self.blacklisted.update({user["id"]: user["reason"]})

    def template(self, record: asyncpg.Record):
        return {record["id"]: dict(record)}

    async def refresh_cache_for(self, id: int):
        config = await self.db.fetchrow("SELECT * FROM config WHERE id = $1", id)
        self.cache.update({config["id"]: dict(config)})

    async def on_error(self, event_method, *args, **kwargs):
        self._logger.error(f"An Error Occurred: \n {event_method}\n")

        etype, exc, trace = sys.exc_info()

        lines = traceback.format_exception(etype, exc, trace)

        self._logger.error("".join(lines))

    def add_cog(self, cog):
        super(HarleyBot, self).add_cog(cog)

        if (aliases := getattr(cog, "aliases", None)) is not None:
            for alias in aliases:
                self._BotBase__cogs[alias] = cog

    def remove_cog(self, name):

        cog = self.get_cog(name)

        super(HarleyBot, self).remove_cog(name)

        if (aliases := getattr(cog, "aliases", None)) is not None:
            for alias in aliases:
                self._BotBase__cogs.pop(alias)

    def load_cogs(self):
        logger = logging.getLogger("cogs")

        for cog in self.config["cogs"]:
            try:
                self.load_extension(cog)
                logger.info(f"Loaded {cog}")
            except Exception as e:
                logger.exception(f"{cog} failed to load")

    def run(self, token: str = None) -> None:
        return super().run(
            token or self.config["token"],
        )

    async def on_ipc_ready(self):
        self._logger.info("IPC Ready.")

    @property
    def session(self):
        return self._session

    @property
    def hook(self):
        return self._hook

    @property
    def logger(self):
        return self._logger

    @property
    def dagpi(self):
        return self._dagpi


class HarleyContext(commands.Context):
    @property
    def cache(self):
        return self.bot.cache[self.guild.id]

    @property
    def db(self):
        return self.bot.db

    @property
    def mapped_message(self) -> Optional[Message]:
        """Returns the mapped message to this ctx, if any."""
        return self.bot.edit_mapping.get(self.message)

    async def refresh(self):
        await self.bot.refresh_cache_for(self.guild.id)

    def get_role(self, id):
        return self.guild.get_role(id)

    def get_channel(self, id):
        return self.guild.get_channel(id)

    async def reply(self, content=None, **kwargs):

        if self.bot.edit_mapping.get(self.message):

            if "embed" not in kwargs:
                kwargs["embed"] = None  # why, this is literally the same as popping it

            msg = self.bot.edit_mapping.get(self.message)
            await msg.edit(content=content, **kwargs)
            return msg

        msg = await super().reply(content=content, **kwargs)

        self.bot.edit_mapping[self.message] = msg

        return msg

    async def send(self, content=None, **kwargs):

        if self.bot.edit_mapping.get(self.message):
            if "embed" not in kwargs:
                kwargs["embed"] = None

            msg = self.bot.edit_mapping.get(self.message)
            await msg.edit(content=content, **kwargs)
            return msg

        msg = await super().send(content=content, **kwargs)

        self.bot.edit_mapping[self.message] = msg

        return msg

    async def confirm(self, text=None, **kwargs):
        msg = None

        reactions = [
            self.bot.custom_emojis["x-mark"],
            self.bot.custom_emojis["checkmark"],
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
            reaction, user = await self.bot.wait_for(
                "reaction_add",
                check=(
                    lambda r, u: r.message.id == msg.id
                    and u.id == self.author.id
                    and str(r) in reactions
                ),
                timeout=30,
            )
            return bool(reactions.index(str(reaction)))
        except asyncio.TimeoutError:
            await self.reply(
                embed=CustomEmbed(description="You did not react in time.")
            )
            return False


class CustomEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.color = kwargs.get("color", choice([0x4BA893, 0xC46D6C]))
        self.timestamp = kwargs.get("timestamp", discord.utils.utcnow())


# Shamelessly stolen from https://gist.github.com/bencharb/729971d4a9e4633ea08a
class CappedDict(collections.OrderedDict):
    default_max_size = 100

    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop("max_size", self.default_max_size)
        super(CappedDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        if key not in self:
            max_size = (
                self.max_size - 1
            )  # so the dict is sized properly after adding a key
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
