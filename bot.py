# Import Discord Package
import discord
import responses

# Get bot token
TOKEN = 'MTM2MDY5NzY3OTg3MjUyODU5Ng.GykOFH.Ft91vod6vef7pbJvBxWHLbg9-wO4vce1Hfj2vc'

# Getting user input
async def send_message(message, user_message, is_private):
    try:
        response = responses.get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    
    except Exception as e:
        print(e)

# Client 
class MyClient(discord.Client):  # Hover over discord.Client to see all parameters that can be passed for line 18 - "client = MyClient"
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == MyClient.user:
            return

        if message.content[0] == '?':
            message.content = message.content[1:]
            await send_message(message, message.content, is_private=True)   # If a user sends a message starting with ?, the bot will reply in DM
        else:
            await send_message(message, message.content, is_private=False)  # Otherwise reply directly in the channel

        print(f'Message from {message.author}: {message.content}, in channel: {message.channel}')

# Define run function for main.py
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(TOKEN)