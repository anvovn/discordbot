import discord
from discord.ext import commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")
    
    @commands.command()
    async def roll(self, ctx):
        await ctx.send("Games test")

async def setup(bot):
    await bot.add_cog(Roll(bot))