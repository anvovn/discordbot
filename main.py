# Import Discord Package
import discord
from discord.ext import commands
import os
import asyncio

# Initialize bot
TOKEN = 'MTA1NDQ4Njk3NzE5MTM1NDM5OA.GL-cey.6AMgD1HTkwP3D_LFhck1g4DcEZ4x-waOGGRz2g' #'MTM2MDY5NzY3OTg3MjUyODU5Ng.GVL-Sy.rNAxGpPIQ5ly4UAvQsn1cZXqLhIJJGvnzW2AUI'  # Insert token here
GUILD_ID = discord.Object(id=1360030609841590425) # Insert ID here
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot_status = discord.Game("/help for more")

# Bot client
@bot.event
async def on_ready():
    await bot.tree.sync()
    await change_bot_status()
    print(f"{bot.user} is ready (ID: {bot.user.id})")

async def change_bot_status():
    await bot.change_presence(activity=bot_status)

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