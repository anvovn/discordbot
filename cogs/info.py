import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

class Info(commands.Cog):
    def init(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @app_commands.command(name="info", description="Provide Information about the bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="CS 407 Bot",
            url="https://github.com/anvovn/cs407-project",
           description="Github link",
           color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8dm1kH_dIjn2dtMwkgO2wbdHunzc2ayEUZQ&s")
        embed.add_field(name="Commands", value="/info, /roll, /8ball, /weather, /kick, /ban, /clear", inline=False)
        embed.set_footer(text="Creator: An, Tyler")
        embed.set_author(
            name=interaction.user.name,
            url="https://chatgpt.com/?ref=glasp",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else ""
        )
        await interaction.response.send_message(embed=embed)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention} for: {reason}")

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.mention} for: {reason}")

    @app_commands.command(name="clear", description="Clear a number of messages from the current channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Cleared {amount} messages.", ephemeral=True)


OPENWEATHER_API_KEY = "5eafb5d6b8e5e9284d3888ae92b1d32a"
class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")
    
    @app_commands.command(name="weather", description="Display the current weather for a city")
    @app_commands.describe(city="The name of the city to get the weather for")
    async def weather(self, interaction: discord.Interaction, city: str):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await interaction.response.send_message("Could not get weather data. Try again.", ephemeral=True)
                    return
                data = await resp.json()

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        embed = discord.Embed(
            title=f"Weather in {city.title()}",
            description=f"{weather}",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌡️ Temperature", value=f"{round(temp*(9/5)+32,1)}°F (feels like {round(feels_like*(9/5)+32,1)}°F)", inline=False)
        embed.add_field(name="💧 Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="💨 Wind Speed", value=f"{wind_speed} m/s", inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(Weather(bot))