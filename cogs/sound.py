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
    @app_commands.command(name='sb', description= 'Play music')
    @app_commands.describe()
    async def sb(self, interaction: discord.Interaction):
        await interaction.response.send_message("Soundboard test")

class MusicButtons(discord.ui.View):
    pass

async def setup(bot):
    await bot.add_cog(Sound(bot))