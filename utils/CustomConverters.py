import datetime
import re

import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter
from discord.ext.commands.errors import BadArgument, CommandError, MemberNotFound

from utils.enums import LoggingEnum


class HierarchyMemberConverter(commands.Converter):
    async def convert(self, ctx, argument) -> discord.Member:
        try:
            member = await MemberConverter().convert(ctx, argument)

            if member == ctx.guild.owner:
                raise BadArgument("This member owns the guild.")

            elif member == ctx.author:
                raise BadArgument("You cannot preform this action on yourself.")

            elif member.top_role >= ctx.author.top_role:
                raise BadArgument(
                    "The given member's top role is either equal or higher than yours in the hierarchy!"
                )

            elif member.top_role >= ctx.me.top_role:
                raise BadArgument(
                    "The given member's top role is either equal or higher than mine in the hierarchy!"
                )

            return member

        except (CommandError, MemberNotFound) as e:
            raise e


time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument) -> datetime.datetime:
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(
                    "{} is an invalid time-key! h/m/s/d are valid!".format(k)
                )
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=time)


class OptionsConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.upper().replace(" ", "_") in LoggingEnum.__members__:
            raise commands.BadArgument("Not a valid argument.")
        return LoggingEnum[argument.upper()]


class AttachmentConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if attach := ctx.message.attachments:
            return attach[0]

        else:
            raise commands.BadArgument("No attachment provided.")
