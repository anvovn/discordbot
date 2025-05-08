import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")
    
    @commands.command()
    async def info(self, ctx):
        await ctx.send("Commands: !help, !roll")

async def setup(bot):
    await bot.add_cog(Info(bot))