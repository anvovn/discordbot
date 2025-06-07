import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp

class Sound(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'default_search': 'ytsearch'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")
    
    # Music playback 
    @app_commands.command(name='play', description= 'Play music')
    @app_commands.describe(song_query="Search song")
    async def play(self, interaction: discord.Interaction, song_query: str):
        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel if interaction.user.voice else None

        if not voice_channel:
            await interaction.followup.send("You must join a voice channel first.")
            return

        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url=f"ytsearch:{song_query}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail')
            self.queue.append((url, title, thumbnail))
            await interaction.followup.send(f"Added to queue: **{title}**")

        if not voice_client.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if self.queue:
            url, title, thumbnail = self.queue.pop(0)
            source = discord.FFmpegOpusAudio(url, **self.FFMPEG_OPTIONS)

            def after_playing(error):
                if error:
                    print(f"Playback error: {error}")
                fut = asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error calling play_next: {e}")

            # Music status
            voice_client.play(source, after=after_playing)
            embed = discord.Embed(
                    title = title,
                    description=f"Now Playing **{title}**",
                    url=url,
                    color=discord.Color.dark_gold()
            )
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=f"Req. by {interaction.user.name}", icon_url=interaction.user.avatar.url)
            view = MusicButtons(self)
            await interaction.followup.send(embed=embed, view=view)

        elif not voice_client.is_playing():
            await interaction.followup.send("Queue is empty!")

class MusicButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.primary)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.followup.send("Playback Resumed!", ephemeral=True)
        else:
            await interaction.followup.send("Music is Already Playing", ephemeral=True)
            return

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.followup.send("Playback Paused!", ephemeral=True)
        else:
            await interaction.followup.send("Music is Currently Paused", ephemeral=True)
            return
            
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.grey)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            await interaction.followup.send("I'm not connected to a voice channel.", ephemeral=True)
            return

        if not voice_client.is_playing():
            await interaction.followup.send("No song is currently playing.", ephemeral=True)
            return

        voice_client.stop()
        await interaction.followup.send("Skipped the current song!", ephemeral=True)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.defer()

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.followup.send("Successfully Disconnected.", ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Sound(bot))