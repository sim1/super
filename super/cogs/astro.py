import random
import time

import aiohttp

import structlog
from discord import Embed
from discord.ext import commands
from super.utils import fuz, owoify, superheroes

logger = structlog.getLogger(__name__)


class Astro(commands.Cog):
    """Horoscope"""

    def __init__(self, bot):
        self.bot = bot
        self.sunsigns = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]
        self.times = ("today", "yesterday", "tomorrow")
        self.api = "https://aztro.sameerkumar.website/?sign={sunsign}&day={when}"
        self.seed = random.random()

    async def _get_sunsign(self, sunsign, when):
        logger.debug("cogs/astro/_get_sunsign: Fetching", sunsign=sunsign, when=when)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api.format(sunsign=sunsign, when=when),
                timeout=5,
            ) as resp:
                return await resp.json()

    async def _astro(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            message = ctx.message.content.split(" ")

            if len(message) >= 2:
                logger.debug("cogs/astro/_astro: Fetching", message=message[1])
                sunsign = fuz(message[1], self.sunsigns, threshold=1)
            else:
                return await ctx.message.channel.send(
                    ".astro <sign> [**today**|yesterday|tomorrow]"
                )

            when = fuz(
                message[2] if len(message) >= 3 else "today", self.times, "today"
            )

            title = f"{when}'s horoscope for {sunsign}"
            data = await self._get_sunsign(sunsign, when)
            horoscope = data["description"]
            random.seed(horoscope)

            truth_mode = random.random() < 0.05
            if truth_mode:
                horoscope = "The stars and planets will not affect your life in any way."
            else:
                horoscope = horoscope.replace("Ganesha", random.choice(superheroes))

            random.seed(self.seed + time.time())  # a caso

            logger.info("cogs/astro/_astro: Fetched", sunsign=sunsign)
            if owo:
                horoscope = owoify(horoscope)
                title = owoify(title)
            
            e = Embed(title=title, type="rich", description=horoscope)

            if not truth_mode:
                for key, value in data.items():
                    if key in ("description", "current_date", "description"):
                        continue
                    key, value = key.lower().replace("_", " "), value.lower()
                    if owo:
                        key, value = owoify(key), owoify(value)
                    e.add_field(name=key, value=value, inline=True)

            return e

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """**.astro** <sign> [today|week|month|year] - Daily dose of bullshit"""
        return await ctx.message.channel.send(embed=await self._astro(ctx))

    @commands.command(no_pm=True, pass_context=True)
    async def astrowo(self, ctx):
        """**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit"""
        return await ctx.message.channel.send(embed=await self._astro(ctx, owo=True))


def setup(bot):
    bot.add_cog(Astro(bot))
