import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")
    
    @commands.command()
    async def play(self, ctx):
        await ctx.send("Test")

async def setup(bot):
    await bot.add_cog(Music(bot))