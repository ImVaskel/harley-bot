import logging
import traceback
from functools import cached_property

from discord.ext import commands, flags
from utils.CustomErrors import Blacklisted
from utils.subclasses import CustomEmbed

CODEBLOCK = "```fix\n{}```"

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_errors = (
            commands.CommandNotFound,
        )
        self.str_errors = (
            commands.NotOwner, commands.BadArgument, commands.MissingRequiredArgument, commands.CommandOnCooldown, Blacklisted, commands.MissingPermissions,
            commands.BotMissingPermissions, commands.TooManyArguments, flags.ArgumentParsingError, commands.BadUnionArgument
        )

        self._logger = logging.getLogger("Command Error")

    @cached_property
    def logger(self):
        return self._logger


    @commands.Cog.listener('on_command_error')
    async def command_error(self, ctx: commands.Context, error):

        error = getattr(error, "original", error)

        if isinstance(error, self.ignored_errors):
            return

        conditions = (
            ctx.command is not None and ctx.command.has_error_handler(),
            ctx.command.parent is not None and ctx.command.parent.has_error_handler()
        )

        if any(conditions):
            return

        elif isinstance(error, self.str_errors):
            return await ctx.reply(embed= CustomEmbed(
                description = str(error)
            ))
                
        else:

            traceback_text = "".join(traceback.format_exception(type(error), error, error.__traceback__, 4))

            await ctx.reply(embed = CustomEmbed(
                title = "An error has occurred.",
                description= "```\n" + str(error) + "```"
            ).set_footer(text="I have reported it to the developers."))

            paste = await self.bot.utils.paste(traceback_text, syntax="py")

            await self.bot.hook.send(embed = CustomEmbed(
                description = f"An error occurred! \n URL: {paste}"
            ).set_footer(text=f"Caused by {ctx.command}"), username=str(ctx.author), avatar_url=ctx.author.avatar_url
            )

            self.logger.exception(f"{ctx.command.name} \n{traceback_text}")

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
