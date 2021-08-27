import markdown
from discord.ext import commands
from utils import Embed

DATETIME_STR = "%y-%m-%d"


class Fun(commands.Cog):
    """Module focused on fun"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def apod(self, ctx, date=None):
        """An astronomy picture of the day from NASA's api. Use `YYYY-MM-DD` for the date or the latest will be pulled."""

        url = (
            f"https://api.nasa.gov/planetary/apod?date={date}&api_key={self.bot.config['nasa']}"
            if date is not None
            else f"https://api.nasa.gov/planetary/apod?api_key={self.bot.config['nasa']}"
        )

        json = await (await self.bot.session.get(url)).json()

        if error := json.get("msg"):
            return await ctx.reply(embed=Embed(title="Error", description=error))

        await ctx.reply(
            embed=Embed(
                title=json.get("title", "None"),
                description=json.get("explanation", "No explanation"),
            ).set_image(url=json.get("url"))
        )

    @commands.command()
    async def xkcd(self, ctx, comic=None):
        """Returns the given xkcd comic or the newest one, depending on if `comic` is passed."""

        url = (
            f"http://xkcd.com/{comic}/info.0.json"
            if comic
            else "http://xkcd.com/info.0.json"
        )

        async with ctx.bot.session.get(url) as res:
            if res.status == 404:
                return await ctx.reply(embed=Embed(description="Invalid comic."))

            res = await res.json()

            await ctx.reply(
                embed=Embed(
                    title=f"Comic {comic or res['num']}",
                    description=res.get("alt", "No alt text"),
                ).set_image(url=res.get("img"))
            )

    @commands.command()
    async def markdown(self, ctx, *, text):
        """Performs markdown on the given text"""
        code = markdown.markdown(text)
        url = None

        if len(code) > 512:
            url = await self.bot.utils.paste(code, syntax="html")

        await ctx.reply(embed=Embed(description=url or f"```html\n{code}```"))


def setup(bot):
    bot.add_cog(Fun(bot))
