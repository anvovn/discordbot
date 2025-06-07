import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import asyncio
import os
import requests
import json
import random
from datetime import datetime, timedelta
import statistics
from dotenv import load_dotenv
from pathlib import Path
from discord import app_commands, Interaction, Embed, Color
from discord.ui import Button, View

OPENWEATHER_API_KEY = "5eafb5d6b8e5e9284d3888ae92b1d32a"

class Info(commands.Cog):
    def init(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    # Info
    @app_commands.command(name="info", description="Provide Information about the bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="CS 407 Bot",
            url="https://github.com/anvovn/cs407-project",
           description="Github link",
           color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8dm1kH_dIjn2dtMwkgO2wbdHunzc2ayEUZQ&s")
        embed.add_field(name="Commands", value=f"/8ball, /ban, /blackjack, /clear, /info, /kick, /play, /poker, /reminder, /roll, /weather", inline=False)
        embed.set_footer(text="Creator: An, Tyler")
        embed.set_author(
            name=interaction.user.name,
            url="",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else ""
        )
        await interaction.response.send_message(embed=embed)

    # Reminders
    @app_commands.command(name="reminder", description="Set a reminder")
    @app_commands.describe(action="Describe the task", minutes="Enter minutes", seconds="Enter seconds")
    async def remind(self, interaction: discord.Interaction, action: str, minutes: int, seconds: int):
        await interaction.response.send_message(f"Reminder: \"{action}\", set for {minutes} minutes and {seconds} seconds!")
        await asyncio.sleep(minutes * 60 + seconds)
        await interaction.followup.send(f"Time to {action} {interaction.user.mention}!")

    # Get weather
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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    # Kick
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention} for: {reason}")

    # Ban
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.mention} for: {reason}")

    # Clear msgs
    @app_commands.command(name="clear", description="Clear a number of messages from the current channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Cleared {amount} messages.", ephemeral=True)

ALPHA_VANTAGE_API_KEY = "Q2V7FMJ8LM7I8RG2"

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stock", description="Get stock price and trends")
    @app_commands.describe(symbol="Stock symbol (e.g. AAPL, MSFT)")
    async def stock(self, interaction: discord.Interaction, symbol: str):
        await interaction.response.defer()
        
        # API endpoints
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        daily_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"

        try:
            async with aiohttp.ClientSession() as session:
                # Get current quote
                async with session.get(quote_url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("Could not fetch stock data. Please try again later.")
                        return
                    quote_data = await resp.json()
                
                # Get historical data
                async with session.get(daily_url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("Could not fetch historical data.")
                        return
                    history_data = await resp.json()

            # Process current quote
            if "Global Quote" not in quote_data:
                await interaction.followup.send(f"Could not find stock symbol {symbol}")
                return
                
            quote = quote_data["Global Quote"]
            price = float(quote["05. price"])
            change = float(quote["09. change"])
            change_percent = quote["10. change percent"]
            
            # Process historical data
            if "Time Series (Daily)" not in history_data:
                await interaction.followup.send("Could not fetch historical prices")
                return
                
            daily_data = history_data["Time Series (Daily)"]
            dates = sorted(daily_data.keys(), reverse=True)[:5]  # Last 5 trading days
            prices = [float(daily_data[date]["4. close"]) for date in dates]
            
            # Calculate trend
            trend = "⬆️" if prices[0] > prices[-1] else "⬇️"
            trend_percent = abs((prices[0] - prices[-1]) / prices[-1] * 100)
            
            # Create embed
            embed = Embed(
                title=f"📈 {symbol.upper()} Stock Information",
                color=0x00ff00 if change > 0 else 0xff0000  # Green if up, red if down
            )
            embed.add_field(name="Current Price", value=f"${price:.2f}", inline=True)
            embed.add_field(name="Change", value=f"{change:.2f} ({change_percent})", inline=True)
            embed.add_field(name="5-Day Trend", value=f"{trend} {trend_percent:.2f}%", inline=True)
            
            # Add price history
            history_text = "\n".join([f"{date}: ${price:.2f}" for date, price in zip(dates, prices)])
            embed.add_field(name="Recent Prices", value=history_text, inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            await interaction.followup.send("An error occurred while fetching stock data.")


async def setup(bot):
    await bot.add_cog(Info(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(Stocks(bot))