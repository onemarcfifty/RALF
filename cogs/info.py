import time
import os

from discord.ext import commands

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 Pong: {before_ws}ms  |  REST: {int(ping)}ms")

async def setup(bot):
    await bot.add_cog(Information(bot))
