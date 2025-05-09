import discord
from discord.ext import commands
from discord import app_commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} ready")
    
    @commands.command()
    async def roll(self, ctx):
        await ctx.send("Games test")
    
    @app_commands.command(name="roll", description="Testser roll")
    async def roll(self, interaction: discord.Interaction):
        await interaction.response.send_message("Games test")

async def setup(bot):
    await bot.add_cog(Roll(bot))