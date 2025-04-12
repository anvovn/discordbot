# Import Discord Package
import discord
import responses

# Client
class MyClient(discord.Client):  # Hover over discord.Client to see all parameters that can be passed for line 18 - "client = MyClient"
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

# Define run function for main.py
def run_discord_bot():
    TOKEN = 'MTM2MDY5NzY3OTg3MjUyODU5Ng.GykOFH.Ft91vod6vef7pbJvBxWHLbg9-wO4vce1Hfj2vc'
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(TOKEN)