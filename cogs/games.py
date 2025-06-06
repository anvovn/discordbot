import discord
from discord.ext import commands
from discord import app_commands, Interaction
from treys import Card, Deck, Evaluator
import asyncio
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {} # Poker

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

    # Poker
    @app_commands.command(name="poker", description="Start a multiplayer poker game with betting")
    async def poker(self, interaction: discord.Interaction):
        if interaction.channel.id in self.active_games:
            await interaction.response.send_message("Game already in progress.", ephemeral=True)
            return
        
        game = PokerGame()
        game.channel = interaction.channel
        self.active_games[interaction.channel.id] = game
        view = PokerView(game)

        await interaction.response.send_message("Poker game starting! Click to join:", view=view)

        await asyncio.sleep(10)  # wait for players to join

        if len(game.players) < 2:
            await interaction.followup.send("Not enough players to start the game.")
            del self.active_games[interaction.channel.id]
            return

        game.started = True

        while (game.started):
            game.deal()
            game.board = []
            game.current_bet = 0
            game.pot = 0

            for player in game.players:
                if player.balance != 0:
                    player.folded = False
                player.current_bet = 0

            for player in game.players:
                hand_str = " ".join(Card.int_to_pretty_str(c) for c in player.hand)
                await player.user.send(f"Your hand: {hand_str}")

            for round_num in range(3):  # Pre-flop, Turn, River
                game.betting_round = round_num
                game.deal_board()

                board_cards = " ".join(Card.int_to_pretty_str(c) for c in game.board)
                await interaction.followup.send(f"Board after round {round_num + 1}: {board_cards}")

                await self.run_betting_round(game)

            results = game.evaluate()

            embed = discord.Embed(title="🃏 Poker Results", color=discord.Color.gold())
            board_cards = " ".join(Card.int_to_pretty_str(c) for c in game.board)
            embed.add_field(name="Community Cards", value=board_cards, inline=False)

            for score, player in results:
                if not player.folded:
                    hand_str = " ".join(Card.int_to_pretty_str(c) for c in player.hand)
                    embed.add_field(name=player.user.display_name, value=f"Hand: {hand_str}\nScore: {score}", inline=False)
                else:
                    embed.add_field(name=player.user.display_name, value="Folded", inline=False)

            winner = results[0][1]
            embed.add_field(name="Winner", value=f"🏆 {winner.user.mention} wins the pot of ${game.pot}!", inline=False)
            winner.balance += game.pot
            await interaction.followup.send(embed=embed)

            tmp = []
            stats = []
            for player in game.players:
                if player.balance == 0:
                    stats.append(f"Player: {player.user}, Balance: {player.balance} -> OUT")
                else:
                    stats.append(f"Player: {player.user}, Balance: {player.balance} -> IN")
                    tmp.append(player)
            
            await interaction.followup.send("\n".join(stats))
            game.players = tmp

            # Play again
            view = PokerEndView(game)
            await interaction.followup.send("Please wait until the next round starts, otherwise hit leave", view=view)

            await asyncio.sleep(10)  # wait for players to join

            if len(game.players) < 2:
                await interaction.followup.send("Not enough players to start the game.")
                del self.active_games[interaction.channel.id]
                game.started = False
            
        del self.active_games[interaction.channel.id]

    async def run_betting_round(self, game):
        active_players = [p for p in game.players if not p.folded and p.balance > 0]

        for player in active_players:
            if player.folded:
                continue

            call_amount = game.current_bet - player.current_bet

            # Skip players who are already all-in
            if player.balance <= 0:
                continue

            def check(m):
                return m.author == player.user and m.channel == game.channel

            await game.channel.send(
                f"{player.user.mention}, the current bet is ${game.current_bet}. "
                f"Your balance: ${player.balance}. Your current bet: ${player.current_bet}. "
                "Type 'call', 'raise <amount>', or 'fold'."
            )

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
                content = msg.content.lower()

                if content.startswith("fold"):
                    player.folded = True

                elif content.startswith("call"):
                    if call_amount > player.balance:
                        # All-in scenario
                        game.pot += player.balance
                        player.current_bet += player.balance
                        player.balance = 0
                        await game.channel.send(f"{player.user.mention} goes all-in!")
                    else:
                        player.balance -= call_amount
                        player.current_bet += call_amount
                        game.pot += call_amount

                elif content.startswith("raise"):
                    parts = content.split()
                    if len(parts) == 2 and parts[1].isdigit():
                        raise_amt = int(parts[1])
                        total_to_call_and_raise = call_amount + raise_amt

                        if total_to_call_and_raise > player.balance:
                            await game.channel.send(f"{player.user.mention}, not enough balance to raise ${raise_amt}. You folded.")
                            player.folded = True
                        else:
                            player.balance -= total_to_call_and_raise
                            player.current_bet += total_to_call_and_raise
                            game.pot += total_to_call_and_raise
                            game.current_bet = player.current_bet
                    else:
                        await game.channel.send("Invalid raise format. Type 'raise <amount>'. You folded.")
                        player.folded = True

                else:
                    await game.channel.send("Invalid action. You folded by default.")
                    player.folded = True

            except asyncio.TimeoutError:
                await game.channel.send(f"{player.user.mention} took too long and folded.")
                player.folded = True

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

class PokerPlayer:
    def __init__(self, user):
        self.user = user
        self.hand = []
        self.balance = 1000
        self.current_bet = 0
        self.folded = False

class PokerGame:
    def __init__(self):
        self.players = []
        self.started = False
        self.deck = Deck()
        self.board = []
        self.evaluator = Evaluator()
        self.pot = 0
        self.current_bet = 0
        self.betting_round = 0
        self.channel = None

    def add_player(self, user):
        if self.started or any(p.user == user for p in self.players):
            return False
        self.players.append(PokerPlayer(user))
        return True

    def del_player(self, user):
        for player in self.players:
            if player.user == user:
                self.players.remove(player)
                return True
        return False

    def deal(self):
        for player in self.players:
            player.hand = [self.deck.draw(1)[0] for _ in range(2)]

    def deal_board(self):
        if self.betting_round == 0:
            self.board += [self.deck.draw(1)[0] for _ in range(3)]
        elif self.betting_round in [1, 2]:
            self.board.append(self.deck.draw(1)[0])

    def evaluate(self):
        results = []
        for player in self.players:
            if not player.folded:
                score = self.evaluator.evaluate(self.board, player.hand)
                results.append((score, player))
        results.sort()
        return results
    
class PokerView(discord.ui.View):
    def __init__(self, game, timeout=30):
        super().__init__(timeout=timeout)
        self.game = game

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if self.game.add_player(user):
            await interaction.response.send_message(f"{user.mention} joined the game!")
        else:
            await interaction.response.send_message("You're already in or game has started.", ephemeral=True)
            
class PokerEndView(discord.ui.View):
    def __init__(self, game, timeout=30):
        super().__init__(timeout=timeout)
        self.game = game

    @discord.ui.button(label="Leave Game", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if self.game.del_player(user):
            await interaction.response.send_message(f"{user.mention} has left the game!")
        else:
            await interaction.response.send_message("You've already left the game.", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Games(bot))