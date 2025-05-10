import discord
from discord.ext import commands
from discord import app_commands, Interaction
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} ready")

    # Roll number
    @app_commands.command(name="roll", description="Rolls a random number between 1 and the given number.")
    @app_commands.describe(number="Max number(e.g. 10 -> roll 1-10).")
    async def roll(self, interaction: discord.Interaction, number: int):
        """Rolls a number between 1 and the given number."""
        if number < 1:
            await interaction.response.send_message("Enter a number greater than 0.")
            return
        result = random.randint(1, number)
        await interaction.response.send_message(f"🎲 **{result}**")

    # 8ball
    @app_commands.command(name="8ball", description="Yes / No / Maybe")
    async def eightball(self, interaction: discord.Interaction):
        result = random.choice(["Yes", "No", "Maybe", "Definitely", "Absolutely not"])
        await interaction.response.send_message(result)

    # Blackjack
    @app_commands.command(name="blackjack", description="Play a simple blackjack game")
    async def blackjack(self, interaction: discord.Interaction):
        def draw_card():
            cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            return random.choice(cards)

        def hand_value(hand):
            value = 0
            aces = 0
            for card in hand:
                if card in ['J', 'Q', 'K']:
                    value += 10
                elif card == 'A':
                    aces += 1
                    value += 11
                else:
                    value += int(card)
            while value > 21 and aces:
                value -= 10
                aces -= 1
            return value

        player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]

        async def show_hands(hidden=True):
            dealer_display = f"{dealer_hand[0]} ?" if hidden else " ".join(dealer_hand)
            return (
                f"**Your hand:** {' '.join(player_hand)} (Total: {hand_value(player_hand)})\n"
                f"**Dealer's hand:** {dealer_display}"
            )

        await interaction.response.send_message(await show_hands(), view=BlackjackButtons(player_hand, dealer_hand, show_hands))

class BlackjackButtons(discord.ui.View):
    def __init__(self, player_hand, dealer_hand, show_hands):
        super().__init__()
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.show_hands = show_hands
        self.finished = False

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        card = random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])
        self.player_hand.append(card)

        if self.get_value(self.player_hand) > 21:
            await interaction.response.edit_message(content="You busted!\n" + await self.show_hands(False), view=None)
            self.finished = True
        else:
            await interaction.response.edit_message(content=await self.show_hands(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        while self.get_value(self.dealer_hand) < 17:
            self.dealer_hand.append(random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']))
        
        player_score = self.get_value(self.player_hand)
        dealer_score = self.get_value(self.dealer_hand)

        if dealer_score > 21 or player_score > dealer_score:
            result = "You win!"
        elif player_score == dealer_score:
            result = "It's a tie!"
        else:
            result = "Dealer wins!"

        await interaction.response.edit_message(
            content=f"{result}\n" + await self.show_hands(False),
            view=None
        )
        self.finished = True

    def get_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            if card in ['J', 'Q', 'K']:
                value += 10
            elif card == 'A':
                aces += 1
                value += 11
            else:
                value += int(card)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value
    
async def setup(bot):
    await bot.add_cog(Games(bot))