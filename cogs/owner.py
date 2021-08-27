from typing import Union

import discord
from discord.ext import commands
from discord.member import Member
from discord.user import User
from utils.subclasses import CustomEmbed, HarleyContext


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def dev(self, ctx: commands.Context):
        pass

    @commands.is_owner()
    @dev.command()
    async def reload(self, ctx, cog):

        try:
            self.bot.reload_extension(cog)
            await ctx.reply(
                embed=CustomEmbed(description=f"Reload of `{cog}` successful.")
            )
        except Exception as e:
            await ctx.reply(embed=CustomEmbed(description="```py\n" + str(e) + "```"))

    @dev.command(hidden=True, aliases=["reloadall", "ra"])
    @commands.is_owner()
    async def reload_all(self, ctx):
        successful = []
        unsuccessful = []
        extensions = list(self.bot.extensions.keys())

        for cog in extensions:
            try:
                self.bot.reload_extension(cog)
                successful.append(cog)
            except:
                unsuccessful.append(cog)

        embed = CustomEmbed(title="Reloaded all extensions")

        embed.add_field(name="Successful", value="\t".join(successful) or "None")
        embed.add_field(
            name="Unsuccessful", value="\t".join(unsuccessful) or "None", inline=False
        )

        await ctx.send(embed=embed)

    @commands.is_owner()
    @dev.command(aliases=("clear", "cleanup"))
    async def purge(self, ctx: commands.Context, num: int):
        """Purges my messages in the channel"""
        iterate = ctx.channel.permissions_for(ctx.me).manage_messages

        try:
            msgs = len(
                await ctx.channel.purge(
                    limit=num, check=lambda m: m.author == self.bot.user, bulk=iterate
                )
            )
        except Exception as e:
            await ctx.reply(
                embed=CustomEmbed(title=f"An error occurred. \n ```\n{e}```")
            )

        await ctx.reply(
            embed=CustomEmbed(
                description=f"Deleted {msgs} / {num} possible message(s) \U0001f44d"
            ),
            delete_after=30,
        )

    @dev.command()
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(extension)
            await ctx.reply(
                embed=CustomEmbed(description=f"Loaded extension `{extension}`")
            )

        except Exception as e:
            await ctx.reply(embed=CustomEmbed(description=f"```py\n{e}```"))

    @dev.command()
    async def unload(self, ctx, extension):
        try:
            self.bot.unload_extension(extension)
            await ctx.reply(
                embed=CustomEmbed(description=f"Unloaded extension `{extension}`")
            )
        except Exception as e:
            await ctx.reply(embed=CustomEmbed(description=f"```py\n{e}```"))

    @commands.is_owner()
    @dev.command(aliases=("remove", "del"))
    async def delete(self, ctx: HarleyContext, message: discord.PartialMessage = None):
        """Deletes the given message"""
        if ctx.message.reference is not None:
            message = ctx.message.reference.cached_message
        elif ctx.message.reference is None and message is None:
            raise commands.BadArgument("No input or message reference was given.")
        try:
            await message.delete()
            await ctx.message.add_reaction("\U0001f44d")
        except:
            await ctx.message.add_reaction("\U0001f44e")

    @commands.is_owner()
    @dev.command(aliases=("restart",))
    async def shutdown(self, ctx):
        await ctx.message.add_reaction("\U0001f44b")
        await ctx.bot.close()

    @commands.is_owner()
    @dev.command()
    async def blacklist(
        self, ctx, user: Union[Member, User], *, reason: str = "None Given"
    ):
        try:
            await self.bot.db.execute(
                "INSERT INTO blacklist(id, reason) VALUES($1, $2)", user.id, reason
            )
            await ctx.message.add_reaction("\U0001f44d")
        except:
            await ctx.message.add_reaction("\U0001f44e")

        record = await self.bot.db.fetchrow(
            "SELECT * FROM blacklist WHERE id = $1", user.id
        )

        self.bot.blacklisted.update({record["id"]: record["reason"]})

    @commands.is_owner()
    @dev.command()
    async def unblacklist(self, ctx, user: Union[Member, User]):
        try:
            await self.bot.db.execute("DELETE FROM blacklist WHERE id = $1", user.id)
            await ctx.message.add_reaction("\U0001f44d")
            self.bot.blacklisted.pop(user.id)
        except:
            await ctx.message.add_reaction("\U0001f44e")

    @commands.is_owner()
    @dev.command(name="error")
    async def _error(self, ctx):
        raise ValueError("Test")


def setup(bot):
    bot.add_cog(Owner(bot))
