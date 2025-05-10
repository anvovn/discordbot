import discord
from discord.ext import commands
from discord import app_commands
import random

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")
    
    @commands.command()
    async def roll(self, ctx):
        await ctx.send("Games test")
    
    @app_commands.command(name="roll", description="Rolls a random number between 1 and the given number.")
    @app_commands.describe(number="Max number(e.g. 10 -> roll 1-10).")
    async def roll(self, interaction: discord.Interaction, number: int):
        """Rolls a number between 1 and the given number."""
        if number < 1:
            await interaction.response.send_message("Enter a number greater than 0.")
            return
        result = random.randint(1, number)
        await interaction.response.send_message(f"🎲 **{result}**")

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @app_commands.command(name="8ball", description="Yes / No / Maybe")
    async def yesno(self, interaction: discord.Interaction):
        result = random.choice(["Yes", "No", "Maybe", "Definitely", "Absolutely not"])
        await interaction.response.send_message(result)

async def setup(bot):
    await bot.add_cog(Roll(bot))
    await bot.add_cog(EightBall(bot))