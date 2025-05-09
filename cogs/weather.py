import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

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
    await bot.add_cog(Weather(bot))