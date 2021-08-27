import asyncio
import collections
import datetime
from contextlib import suppress
from typing import Optional

import asyncpg
import discord
from discord.ext import commands, tasks
from utils.CustomConverters import HierarchyMemberConverter, TimeConverter
from utils.subclasses import CustomEmbed

POLL_PERIOD = 900


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aliases = ("Mod",)
        self._queue = collections.deque()
        self.mute_pull.start()

    async def perform_unmute(
        self,
        *,
        member: discord.Member,
        role: discord.Role,
        when: datetime.datetime,
        record: Optional[int] = None,
    ):
        """Sleep and remove the muted role"""
        await discord.utils.sleep_until(when)

        query = """
                DELETE FROM mutes
                WHERE guildId = $1
                AND userid = $2
                """

        with suppress(discord.Forbidden):
            await member.remove_roles(role)

        await self.bot.db.execute(query, member.guild.id, member.id)
        if record is not None:
            self._queue.pop(record)

    def unmute_error(self, task: asyncio.Task) -> Optional[str]:
        """Print our traceback in the event of an error."""

        if task.exception():
            self.bot.logger.exception(task.exception())

    @tasks.loop(seconds=POLL_PERIOD)
    async def mute_pull(self):
        now = datetime.datetime.utcnow()
        later = now + datetime.timedelta(seconds=POLL_PERIOD)

        query = """
                SELECT * FROM mutes
                WHERE guildId = $1
                AND endtime > $2
                AND endtime < $3
                """

        for guild in self.bot.guilds:
            records: list[asyncpg.Record] = await self.bot.db.fetch(
                query, guild.id, now, later
            )

            if not records:
                return

            for record in records:
                record_id: int = record["id"]
                guild: discord.Guild = self.bot.get_guild(record["guildId"])
                member: discord.Member = guild.get_member(record["userId"])
                role: discord.Role = guild.get_role(
                    self.bot.cache[guild.id]["muted_role"]
                )

                if role is None or member is None:
                    continue

                when: datetime.datetime = record["enddtime"]

                task = self.bot.loop.create_task(
                    self.perform_unmute(member=member, role=role, when=when)
                )
                task.add_done_callback(self.unmute_error)
                self._queue.append(record_id)

    @mute_pull.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: HierarchyMemberConverter,
        force: Optional[bool] = True,
        *,
        reason: Optional[str] = "No reason given",
    ):
        """Kicks a user.
        If ``force`` is True, then it kicks without notifying.
        """

        notified = False

        if force is True:
            try:
                await member.kick(reason=reason)
                notified = False
                await ctx.reply(
                    embed=CustomEmbed(
                        title="Kicked User",
                        description=f"Kicked member {member.name} for reason `{reason}`. User was {'notified.' if notified is True else 'not notified.'}",
                    )
                )
            except:
                return await ctx.send(
                    embed=CustomEmbed(
                        description="I was unable to kick the user for whatever reason."
                    )
                )

        try:
            await member.send(
                embed=CustomEmbed(
                    title="Kicked",
                    description=f"You have been kicked from {ctx.guild.name} by moderator {ctx.author.name} for the reason `{reason}`.",
                )
            )
            notified = True

        except discord.Forbidden:
            notified = False

        finally:
            await member.kick(reason=reason)

            await ctx.reply(
                embed=CustomEmbed(
                    title="Member Kicked",
                    description=f"Kicked member {member.name} for reason `{reason}`. User was {'notified.' if notified is True else 'not notified.'}",
                )
            )

    @flags.add_flag(
        "--force", action="store_true", help="Forces a ban without notifying the user."
    )
    @flags.add_flag("--reason", help="The reason for the ban.")
    @flags.add_flag(
        "--delete",
        type=int,
        default=1,
        help="The number of days worth of messages to delete from the member. Max is 7.",
    )
    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: HierarchyMemberConverter,
        force: Optional[bool] = False,
        delete: Optional[int] = 1,
        *,
        reason: Optional[str] = "None given",
    ):

        notified = False

        if force is True:
            try:
                await member.ban(reason=reason, delete_message_days=delete)
                notified = False
                await ctx.reply(
                    embed=CustomEmbed(
                        title="Banned User",
                        description=f"Banned member {member.name} for reason `{reason}`. User was {'notified.' if notified is True else 'not notified.'}",
                    )
                )
            except:
                return await ctx.send(
                    embed=CustomEmbed(
                        description="I was unable to ban the user for whatever reason."
                    )
                )

        try:
            await member.send(
                embed=CustomEmbed(
                    title="Banned",
                    description=f"You have been banned from {ctx.guild.name} by moderator {ctx.author.name} for the reason `{reason}`.",
                )
            )
            notified = True

        except discord.Forbidden:
            notified = False

        finally:
            await member.ban(reason=reason, delete_message_days=delete)

            await ctx.reply(
                embed=CustomEmbed(
                    title="Member Banned",
                    description=f"Banned member {member.name} for reason `{reason}`. User was {'notified.' if notified is True else 'not notified.'}",
                )
            )

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def softban(
        self,
        ctx,
        member: HierarchyMemberConverter,
        *,
        reason: Optional[str] = "None given",
    ):
        """Bans and unbans a user, thusly deleting their messages."""

        await member.ban(reason=reason)
        await member.unban()

        await ctx.reply(
            embed=CustomEmbed(
                title="Member Softbanned", description=f"Softbanned user {member}."
            )
        )

    @commands.command()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def mute(
        self,
        ctx,
        member: HierarchyMemberConverter,
        time: TimeConverter,
        *,
        reason="None Given",
    ):
        """
        Mutes a member for the specified time format is `6d`

        Valid time specifiers are `d`, `m`, `s`, `h`
        """
        muted_role = ctx.guild.get_role(ctx.cache.get("muteid"))

        if muted_role is None:
            raise commands.BadArgument(
                "I cannot find the muted role in the config, this is probably because the role was deleted."
            )

        if muted_role >= ctx.me.top_role:
            raise commands.BadArgument(
                "The muted role is greater than or equal to my top role in the hierarchy, please move my role above it."
            )

        if muted_role in member.roles:
            await ctx.reply(
                embed=CustomEmbed(
                    description="User was already muted, changing the mute to the new time."
                )
            )
            await member.remove_roles(muted_role, reason="Unmuting")
            await ctx.db.execute(
                "DELETE FROM mutes WHERE guildid = $1 and userid = $2",
                ctx.guild.id,
                member.id,
            )
        sleep = (time - datetime.datetime.utcnow()).total_seconds()
        if sleep <= 1800:
            task = self.bot.loop.create_task(
                self.perform_unmute(
                    member=member, role=muted_role, when=time, record=None
                )
            )
            task.add_done_callback(self.unmute_error)

        await ctx.db.execute(
            "INSERT INTO mutes(userid, guildid, starttime, endtime, reason) VALUES($1, $2, $3, $4, $5)",
            member.id,
            ctx.guild.id,
            datetime.datetime.utcnow(),
            time,
            reason,
        )

        await member.add_roles(
            muted_role, reason=f"Mute done by {ctx.author} [{ctx.author.id}]"
        )

        await ctx.reply(
            embed=CustomEmbed(
                description=(f"Muted {member}\n" f"For Reason: `{reason}`\n"),
                timestamp=time,
            ).set_footer(text="Ends at")
        )

    @commands.command()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def unmute(self, ctx, member: HierarchyMemberConverter):
        """
        Unmutes a member.
        """

        muted_role = ctx.guild.get_role(ctx.cache.get("muteid"))

        if muted_role is None:
            raise commands.BadArgument(
                "I cannot find the muted role in the config, this is probably because the role was deleted or you haven't set it up."
            )

        if muted_role >= ctx.me.top_role:
            raise commands.BadArgument(
                "The muted role is greater than or equal to my top role in the hierarchy, please move my role above it."
            )

        if muted_role in member.roles:
            await member.remove_roles(
                muted_role, reason=f"Unmute done by {ctx.author} [{ctx.author.id}]"
            )
            await ctx.db.execute(
                "DELETE FROM mutes WHERE userid = $1 and guildid = $2",
                member.id,
                ctx.guild.id,
            )
            await ctx.reply(embed=CustomEmbed(description=f"Unmuted {member}"))

        else:
            raise commands.BadArgument(
                "That user doesn't seem to have the `muted` role set in the config."
            )


def setup(bot):
    bot.add_cog(Moderator(bot))
