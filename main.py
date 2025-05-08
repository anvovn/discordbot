# Import Discord Package
import responses
import discord
from discord.ext import commands

# Initialize bot
TOKEN = 'MTM2MDY5NzY3OTg3MjUyODU5Ng.GXOaZJ.0ZbdA4C91ndaJv_qSuw-YA9daq3XVCTgQI_HIg'
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# Bot client
@client.event
async def on_ready():
    print("Bot ready")

@client.command()
async def info(ctx):
    await ctx.send("Commands: !help, ")

# Run bot
if __name__ == '__main__':
    client.run(TOKEN)