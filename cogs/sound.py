import discord
from discord.ext import commands
from discord import app_commands

class Sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")
    
    # Music playback
    @app_commands.command(name='play', description= 'Play music')
    @app_commands.describe()
    async def play(self, interaction: discord.Interaction):
        await interaction.response.send_message("Music test")

    # Soundboard
    # @app_commands.command()
    # async def sb(self, ctx):
    #     await ctx.send("Soundboard test")

async def setup(bot):
    await bot.add_cog(Sound(bot))