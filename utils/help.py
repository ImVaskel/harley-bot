import asyncio
import json
import discord
from discord.ext import commands, menus, flags
from utils.subclasses import CustomEmbed

BLANK_STR = ""
NEWLINE = "\n"
EMOJIS = json.load(open("emojis.json"))

def safe_get(input, index, default=None):
    try:
        return input[index]
    except IndexError:
        return default

class PaginatedHelp(menus.MenuPages, inherit_buttons=False): # type: ignore  ## mypy doesn't like metaclasses.
    def __init__(self, source, **kwargs):
        super().__init__(source, delete_message_after=True, timeout=30, **kwargs)
 
    @menus.button(EMOJIS["information"], position=menus.Last(4))
    async def on_questionmark(self, payload):
        embed = CustomEmbed(
            title = "Help Info",
            description = (
                "```diff\n"
                "- <arg> Required \n"
                "- [arg] Optional \n"
                "- [arg..] Multiple Args\n"
                "```\n"
            )
        )

        embed.add_field(
            name="What do the emojis do?", 
            value = (
                f"{EMOJIS['arrow_left']} - Goes one page backward.\n"
                f"{EMOJIS['double_backward']} - Goes to the first page.\n"
                f"{EMOJIS['stop']} - Stops the menu.\n"
                f"{EMOJIS['double_forward']} - Goes to the last page.\n"
                f"{EMOJIS['arrow_right']} - Goes one page forward\n"
                f"{EMOJIS['information']} - Shows this page.\n"

            )
        )

        if self.source.get_max_pages() == 1:
            embed.set_footer(
                text="To get back to the page, use the double arrows."
            )

        await self.message.edit(embed=embed)
    
    def should_add_reactions(self):
        return True

    @menus.button(EMOJIS["arrow_left"], position=menus.First(2))
    async def left_arrow(self, payload):
        await self.go_to_previous_page(payload)
    
    @menus.button(EMOJIS["stop"], position=menus.First(3))
    async def stop_emoji(self, payload):
        self.stop()
    
    @menus.button(EMOJIS["arrow_right"], position=menus.First(4))
    async def right_arrow(self, payload):
        await self.go_to_next_page(payload)
    
    @menus.button(EMOJIS["double_forward"], position=menus.First(5))
    async def double_forward(self, payload):
        await self.go_to_last_page(payload)

    @menus.button(EMOJIS["double_backward"], position=menus.First(1))
    async def double_backward(self, payload):
        await self.go_to_first_page(payload)

class BotHelpSource(menus.ListPageSource):

    def __init__(self, entries, **options):
        super().__init__(entries, per_page=5)
        self.prefix = options.get("clean_prefix")

    def format_page(self, menu, entries):

        offset = menu.current_page * self.per_page

        embed = CustomEmbed(
            title="Help",
            description = (
                f"Use `{self.prefix}help[command]` for more info on a command.\n"
                f"You can also use `{self.prefix}help[category]` for more info on a category.\n"
            )
        )

        for index, category in enumerate(entries, start=offset):

            cate = list(category.keys())[0]

            category_name = getattr(cate, "qualified_name", "None")

            commands = category.get(list(category.keys())[0])

            aliases = f'[{" | ".join(alias for alias in category.aliases)}]' if getattr(category, 'aliases', None) is not None else ""

            embed.add_field(
                name=f"**{category_name}** [{' | '.join(alias for alias in cate.aliases)}]" if getattr(cate, 'aliases', None)
                is not None else f"**{category_name}**",

                value = f"{getattr(cate, 'description', '')}" + "\n" + " ".join(f'`{command.qualified_name}`' for command in commands) or "`None`",
                inline=False
            )
        embed.set_footer(text=f"Page {menu.current_page + 1} / {self.get_max_pages()}" if
            self.get_max_pages() > 0 else "Page 0/0")
        
        return embed

class CogHelpSource(menus.ListPageSource):
    def __init__(self, cog, data):
        super().__init__(data, per_page=5)
        self.cog = cog

    def format_page(self, menu, entries):

        offset = menu.current_page * self.per_page

        embed = CustomEmbed(
            title=f"{self.cog.qualified_name} " +
            f"[{' | '.join([alias for alias in self.cog.aliases ])}]" if getattr(self.cog, 'aliases', None) is not None else ""
        )

        if (des := getattr(self.cog, "description")) is not None:
            embed.description = des

        for index, command in enumerate(entries, start=offset):
            
            embed.add_field(
                name=f"**{str(command)}** [{' | '.join(alias for alias in command.aliases)}]" if command.aliases else f"**{str(command)}**",
                value=(
                    command.help or "No help given"
                ),
                inline = False
            )
        
        embed.set_footer(text=f"Page {menu.current_page + 1} / {self.get_max_pages()}" if
            self.get_max_pages() > 0 else "Page 0/0")
        
        return embed

class CustomHelp(commands.HelpCommand):
    def __init__(self, **options):

        attrs = {
            "cooldown" : commands.Cooldown(1, 5, commands.BucketType.member),
            "usage" : "help `command, category`",
            "help" : "The help command"
        }

        super().__init__(command_attrs=attrs, **options)
    
    async def send_bot_help(self, mapping):

        filtered_commands = [{key: await self.filter_commands(value)} for key, value in mapping.items() if len(value) != 0]
        clean_prefix = self.clean_prefix

        filtered = []

        for entry in filtered_commands:
            for key, value in entry.items():
                if len(value) != 0:
                    filtered.append({
                        key : value
                    })

        menu = PaginatedHelp(BotHelpSource(filtered, clean_prefix=clean_prefix))
        await menu.start(self.context)
    
    async def send_cog_help(self, cog):
        cmds = [cog, await self.filter_commands(cog.get_commands())]

        menu = PaginatedHelp(CogHelpSource(cmds[0], cmds[1]))
        await menu.start(self.context)
    
    async def send_group_help(self, group):
        cmds = [group, await self.filter_commands(group.commands)]

        menu = PaginatedHelp(CogHelpSource(cmds[0], cmds[1]))
        await menu.start(self.context)

    async def send_command_help(self, command):
        command = await self.filter_commands([command])
        command = safe_get(command, 0)

        if command is None:
            return

        embed = CustomEmbed(
            title="Help"
        )

        embed.add_field(
            name="Help",
            value=command.help or "None",
            inline=False
        )
        embed.add_field(
            name="Aliases",
            value = " ".join("`" + alias + '`' for alias in command.aliases) or "None",
            inline=False
        )
        embed.add_field(
            name="Arguments",
            value = getattr(command, 'usage', getattr(command, 'old_signature', command.signature)) or "None",
            inline=False
        )

        if not isinstance(command, flags.FlagCommand):
            return await self.get_destination().send(embed = embed)

        embed.add_field(
            name="Flags",
            value = (
                "```diff\n"
                f"{NEWLINE.join(f'{flag.option_strings[0]} - {flag.help}' for flag in command.callback._def_parser._actions)}"
                "```"
            )
        )
        await self.get_destination().send(embed = embed)