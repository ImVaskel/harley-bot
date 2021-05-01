import logging

import discord
from discord.ext import commands
from utils.subclasses import CustomEmbed, HarleyBot, HarleyContext

TIME_TEMPLATE = "%b %d, %Y %I:%M %p"
MENTION_TEMPLATE = "<@{}>"

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot: HarleyBot = bot

    @commands.Cog.listener('on_message_edit')
    async def reinvoke_on_edit(self, before, after):
        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            await self.bot.invoke(ctx)
    
    @commands.Cog.listener('on_command')
    async def counter(self, ctx):
        self.bot.usage += 1

    @commands.Cog.listener('on_guild_join')
    async def guild_join(self, guild: discord.Guild):

        await self.bot.db.execute(
            "INSERT INTO config(id) VALUES($1) ON CONFLICT DO NOTHING", guild.id
        )

        await self.bot.refresh_cache_for(guild.id)

        hook = self.bot.hook

        await hook.send(embed = CustomEmbed(
            title="Guild Joined",
            description = (
                "```diff\n"
                f"- Owner: {guild.owner} [{guild.owner.id}] \n"
                f"- Members: {guild.member_count} [{(sum([member.bot for member in guild.members]) / guild.member_count) * 100:.2f}% bots]\n"
                f"- Created: {guild.created_at.strftime(TIME_TEMPLATE)}\n"
                "```"
            )
        ), avatar_url=guild.icon_url, username=guild.name)
    
    @commands.Cog.listener('on_guild_remove')
    async def guild_leave(self, guild: discord.Guild):

        await self.bot.db.execute(
            "DELETE FROM config WHERE id = $1"
        )

        hook = self.bot.logger

        await hook.send(embed = CustomEmbed(
            title="Guild Left",
            description = (
                "```diff\n"
                f"- Owner: {guild.owner} [{guild.owner.id}] \n"
                f"- Members: {guild.member_count} [{(sum([member.bot for member in guild.members]) / guild.member_count) * 1000:.2f}% bots]\n"
                f"- Created: {guild.created_at.strftime(TIME_TEMPLATE)}\n"
                "```"
            )
        ), avatar_url=guild.icon_url, username=guild.name)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f"Logged in as {self.bot.user}")
        self.bot.logger.info(f"Guilds: {len(self.bot.guilds)} Members: {len(self.bot.users)}")

    @commands.Cog.listener('on_message')
    async def reply_with_prefix(self, message):
        if message.author.bot or message.author == self.bot.user:
            return

        if message.content in (MENTION_TEMPLATE.format(f"!{self.bot.user.id}"), MENTION_TEMPLATE.format(
                self.bot.user.id)):

            prefixes = await self.bot.get_prefix(message)

            await message.reply(
                embed=CustomEmbed(
                    description=f"My prefixes are `@Harley ` and `{discord.utils.escape_mentions(prefixes[2])}`."
                )
            )
    
    @commands.Cog.listener('on_message_delete')
    async def delete_message_on_invoking_delete(self, message: discord.Message):
        if message.author.bot or message.author == self.bot.user:
            return
        
        ctx: HarleyContext = await self.bot.get_context(message)

        if ctx.mapped_message is not None:
            await ctx.mapped_message.delete()

            self.bot.edit_mapping.pop(ctx.message.id, None)
    
def setup(bot):
    bot.add_cog(Listeners(bot))
