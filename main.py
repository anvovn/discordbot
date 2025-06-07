# Import Discord Package
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# Initialize bot
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") # Insert token here
keep_alive()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot_status = discord.Activity(type=discord.ActivityType.watching, name=" - /info")
# bot_status = discord.Game("/info for more")

# Bot client
@bot.event
async def on_ready():
    await bot.tree.sync()
    await change_bot_status()
    print(f"{bot.user} is ready (ID: {bot.user.id})")

async def change_bot_status():
    await bot.change_presence(status=discord.Status.dnd, activity=bot_status)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

# Run bot
if __name__ == '__main__':
    asyncio.run(main())