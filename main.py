# Import Discord Package
import discord
from discord.ext import commands
import os
import asyncio

# Initialize bot
TOKEN = 'MTM2MDY5NzY3OTg3MjUyODU5Ng.GXOaZJ.0ZbdA4C91ndaJv_qSuw-YA9daq3XVCTgQI_HIg'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
GUILD_ID = discord.Object(id=1360030609841590425)

# Bot client
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} is ready (ID: {bot.user.id})")

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