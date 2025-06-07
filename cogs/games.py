import discord
from discord.ext import commands
from discord import app_commands, Interaction
from treys import Card, Deck, Evaluator
import asyncio
import random
import json
import random
from dotenv import load_dotenv
from pathlib import Path
from discord import app_commands, Interaction, Embed, Color

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

        cd = 10
        msg = await interaction.followup.send(embed=discord.Embed(description=f"{cd} seconds left to join"), wait=True)
        for i in range(cd + 1):
            updated_embed = discord.Embed(description=f"{cd - i} seconds left to join")
            await msg.edit(embed=updated_embed)
            await asyncio.sleep(1)

        if len(game.players) < 2:
            await msg.edit(content="Not enough players to start the game.", embed=None)
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

            if len(results) == 0:
                await interaction.followup.send(f"No winners. Everybody folded.")
            else:
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
            game.started = False
            view = PokerEndView(game)
            await interaction.followup.send("Please wait until the next round starts, otherwise hit leave", view=view)

            msg = await interaction.followup.send(embed=discord.Embed(description=f"{cd} seconds left to join"), wait=True)
            for i in range(cd + 1):
                updated_embed = discord.Embed(description=f"{cd - i} seconds left to join")
                await msg.edit(embed=updated_embed)
                await asyncio.sleep(1)

            if len(game.players) < 2:
                await interaction.followup.send("Not enough players to start the game.")
                del self.active_games[interaction.channel.id]
            else:
                game.started = True
            
        del self.active_games[interaction.channel.id]

    async def run_betting_round(self, game):
        active_players = [p for p in game.players if not p.folded and p.balance > 0]

        for player in active_players:
            if len(active_players) == 1:
                break

            if player.folded:
                continue

            call_amount = game.current_bet - player.current_bet

            # Skip players who are already all-in
            if player.balance <= 0:
                continue

            def check(m):
                return m.author == player.user and m.channel == game.channel

            while True:
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
                        break

                    elif content.startswith("call"):
                        if call_amount > player.balance:
                            await game.channel.send(f"{player.user.mention}, not enough balance to call ${raise_amt}. Automatic Fold.")
                            player.folded = True
                            break
                        else:
                            player.balance -= call_amount
                            player.current_bet += call_amount
                            game.pot += call_amount
                        break

                    elif content.startswith("raise"):
                        parts = content.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            raise_amt = int(parts[1])
                            total_to_call_and_raise = call_amount + raise_amt

                            if total_to_call_and_raise > player.balance:
                                await game.channel.send(f"{player.user.mention}, not enough balance to raise it by ${raise_amt}. Needs to be at or below ${abs(call_amount - player.balance)}. Try again.")
                                continue
                            else:
                                player.balance -= total_to_call_and_raise
                                player.current_bet += total_to_call_and_raise
                                game.pot += total_to_call_and_raise
                                game.current_bet = player.current_bet
                                break
                        else:
                            await game.channel.send("Invalid raise format. Type 'raise <amount>'. Try again.")
                            continue

                    else:
                        await game.channel.send("Invalid action. Try again.")
                        continue

                except asyncio.TimeoutError:
                    await game.channel.send(f"{player.user.mention} took too long and folded.")
                    player.folded = True
                    break

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

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.green)
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

    @discord.ui.button(label="Join Game (if new)", style=discord.ButtonStyle.green)
    async def join1(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if self.game.add_player(user):
            await interaction.response.send_message(f"{user.mention} joined the game!")
        else:
            await interaction.response.send_message("You're already in or game has started.", ephemeral=True)

    @discord.ui.button(label="Leave Game", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if self.game.del_player(user):
            await interaction.response.send_message(f"{user.mention} has left the game!")
        else:
            await interaction.response.send_message("You've already left the game.", ephemeral=True)
    
class SportsBetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances_file = Path("data/betting_balances.json")
        self.balances_file.parent.mkdir(exist_ok=True)
        self.balances = self._load_balances()
        
        # Team databases with power ratings
        self.nfl_teams = [
            {"name": "Kansas City Chiefs", "power": 85},
            {"name": "Philadelphia Eagles", "power": 83},
            {"name": "Buffalo Bills", "power": 82},
            {"name": "Cincinnati Bengals", "power": 81},
            {"name": "San Francisco 49ers", "power": 84},
            {"name": "Dallas Cowboys", "power": 80},
            {"name": "Miami Dolphins", "power": 79},
            {"name": "Baltimore Ravens", "power": 78},
            {"name": "Los Angeles Chargers", "power": 77},
            {"name": "Minnesota Vikings", "power": 76},
            {"name": "New York Giants", "power": 75},
            {"name": "Detroit Lions", "power": 74}
        ]
        
        self.nba_teams = [
            {"name": "Boston Celtics", "power": 88},
            {"name": "Milwaukee Bucks", "power": 87},
            {"name": "Denver Nuggets", "power": 86},
            {"name": "Phoenix Suns", "power": 85},
            {"name": "Los Angeles Lakers", "power": 84},
            {"name": "Golden State Warriors", "power": 83},
            {"name": "Miami Heat", "power": 82},
            {"name": "Philadelphia 76ers", "power": 81},
            {"name": "Memphis Grizzlies", "power": 80},
            {"name": "Dallas Mavericks", "power": 79},
            {"name": "Brooklyn Nets", "power": 78},
            {"name": "New York Knicks", "power": 77}
        ]

    def _load_balances(self):
        """Load user balances from JSON file"""
        try:
            if not self.balances_file.exists():
                return {}
            with open(self.balances_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading balances: {e}")
            return {}

    def _save_balances(self):
        """Save user balances to JSON file"""
        try:
            with open(self.balances_file, "w") as f:
                json.dump(self.balances, f)
        except Exception as e:
            print(f"Error saving balances: {e}")

    @app_commands.command(name="sportsbet", description="Start a sports betting session")
    async def sports_bet(self, interaction: discord.Interaction):
        """Main betting interface with all options"""
        user_id = str(interaction.user.id)
        
        if user_id not in self.balances:
            self.balances[user_id] = 1000
        
        sport = random.choice(["NFL", "NBA"])
        if sport == "NFL":
            team1, team2 = random.sample(self.nfl_teams, 2)
            total = round(random.uniform(35, 55), 1)
        else:
            team1, team2 = random.sample(self.nba_teams, 2)
            total = round(random.uniform(190, 230), 1)

        # Calculate odds and spread
        power_diff = team1["power"] - team2["power"]
        spread = round(power_diff / 4, 1)
        fav_odds = -150 if power_diff > 5 else -110
        dog_odds = 130 if power_diff > 5 else 110

        # Determine favorite and underdog
        if power_diff > 0:
            favorite = team1["name"]
            underdog = team2["name"]
            fav_spread = f"-{abs(spread)}"
            dog_spread = f"+{abs(spread)}"
        else:
            favorite = team2["name"]
            underdog = team1["name"]
            fav_spread = f"-{abs(spread)}"
            dog_spread = f"+{abs(spread)}"

        # Create embed
        embed = discord.Embed(
            title=f"🏈 {team1['name']} vs {team2['name']}" if sport == "NFL" else f"🏀 {team1['name']} vs {team2['name']}",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Your Balance", value=f"${self.balances[user_id]}", inline=False)
        
        # Moneyline
        embed.add_field(
            name="Moneyline",
            value=f"• {favorite}: {fav_odds}\n• {underdog}: +{dog_odds}",
            inline=False
        )
        
        # Spread
        embed.add_field(
            name="Spread",
            value=f"• {favorite} {fav_spread}\n• {underdog} {dog_spread}",
            inline=False
        )
        
        # Total
        embed.add_field(
            name="Total Points",
            value=f"• Over {total}: -110\n• Under {total}: -110",
            inline=False
        )

        # Store game data
        self.active_game = {
            "user_id": user_id,
            "sport": sport,
            "teams": {
                "team1": team1,
                "team2": team2
            },
            "lines": {
                "moneyline": {
                    favorite: fav_odds,
                    underdog: dog_odds
                },
                "spread": {
                    favorite: fav_spread,
                    underdog: dog_spread
                },
                "total": total
            },
            "power_diff": power_diff
        }

        # Create selection view
        view = BetSelectionView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BetSelectionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog
        self.add_item(BetTypeSelect(cog))

class BetTypeSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        options = [
            discord.SelectOption(label="Moneyline", value="moneyline"),
            discord.SelectOption(label="Spread", value="spread"),
            discord.SelectOption(label="Total", value="total")
        ]
        super().__init__(placeholder="Select bet type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        game = self.cog.active_game
        if self.values[0] == "total":
            # Show over/under selection
            view = discord.ui.View()
            view.add_item(TotalSelect(self.cog))
            await interaction.response.send_message(
                f"Select Over or Under {game['lines']['total']}:",
                view=view,
                ephemeral=True
            )
        else:
            # Show team selection
            view = discord.ui.View()
            view.add_item(TeamSelect(self.cog, self.values[0]))
            await interaction.response.send_message(
                "Select a team:",
                view=view,
                ephemeral=True
            )

class TeamSelect(discord.ui.Select):
    def __init__(self, cog, bet_type):
        self.cog = cog
        self.bet_type = bet_type
        game = cog.active_game
        options = [
            discord.SelectOption(
                label=game["teams"]["team1"]["name"],
                value="team1"
            ),
            discord.SelectOption(
                label=game["teams"]["team2"]["name"],
                value="team2"
            )
        ]
        super().__init__(placeholder="Select team...", options=options)

    async def callback(self, interaction: discord.Interaction):
        game = self.cog.active_game
        selected_team = self.values[0]
        team_name = game["teams"][selected_team]["name"]
        
        # Store the bet selection
        self.cog.active_bet = {
            "type": self.bet_type,
            "selection": team_name,
            "odds": game["lines"][self.bet_type][team_name] if self.bet_type != "spread" else -110
        }
        
        # Ask for bet amount
        await interaction.response.send_message(
            f"Enter your bet amount for {team_name}:",
            ephemeral=True
        )
        
        # Wait for amount input
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
            amount = int(float(msg.content))
            await self.process_bet(interaction, amount)
        except (asyncio.TimeoutError, ValueError):
            await interaction.followup.send("Invalid bet amount", ephemeral=True)

    async def process_bet(self, interaction: discord.Interaction, amount: int):
        user_id = self.cog.active_game["user_id"]
        game = self.cog.active_game
        bet = self.cog.active_bet
        
        # Simulate game outcome
        if game["sport"] == "NFL":
            base = random.randint(10, 30)
            team1_score = base + int(game["power_diff"] * 0.2)
            team2_score = base - int(game["power_diff"] * 0.2)
        else:
            base = random.randint(90, 120)
            team1_score = base + int(game["power_diff"] * 0.3)
            team2_score = base - int(game["power_diff"] * 0.3)
        
        total_score = team1_score + team2_score
        winner = game["teams"]["team1"]["name"] if team1_score > team2_score else game["teams"]["team2"]["name"]
        
        # Calculate payout
        payout = 0
        result_text = ""
        
        if bet["type"] == "moneyline":
            if bet["selection"] == winner:
                payout = amount + (amount * (100/abs(bet["odds"]))) if bet["odds"] < 0 else amount * (bet["odds"]/100)
                result_text = f"✅ {bet['selection']} won! Payout: ${payout:.2f}"
            else:
                result_text = f"❌ {bet['selection']} lost. You lost ${amount}"
        
        elif bet["type"] == "spread":
            spread = float(game["lines"]["spread"][bet["selection"]].replace("+", "").replace("-", ""))
            if "-" in game["lines"]["spread"][bet["selection"]]:  # Favorite
                covered = (team1_score - team2_score) > spread if bet["selection"] == game["teams"]["team1"]["name"] else (team2_score - team1_score) > spread
            else:  # Underdog
                covered = (team2_score - team1_score) < spread if bet["selection"] == game["teams"]["team1"]["name"] else (team1_score - team2_score) < spread
            
            if covered:
                payout = amount + (amount * (100/110))
                result_text = f"✅ {bet['selection']} covered the spread! Payout: ${payout:.2f}"
            else:
                result_text = f"❌ {bet['selection']} didn't cover. You lost ${amount}"
        
        # Update balance
        self.cog.balances[user_id] += payout - amount
        self.cog._save_balances()
        
        # Create result embed
        result_embed = discord.Embed(
            title=f"🎲 {game['teams']['team1']['name']} {team1_score}-{team2_score} {game['teams']['team2']['name']}",
            color=discord.Color.green() if payout > 0 else discord.Color.red()
        )
        result_embed.add_field(name="Result", value=result_text, inline=False)
        result_embed.add_field(name="New Balance", value=f"${self.cog.balances[user_id]:.2f}", inline=False)
        
        await interaction.followup.send(embed=result_embed)

class TotalSelect(discord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        game = cog.active_game
        options = [
            discord.SelectOption(label=f"Over {game['lines']['total']}", value="over"),
            discord.SelectOption(label=f"Under {game['lines']['total']}", value="under")
        ]
        super().__init__(placeholder="Select Over/Under...", options=options)

    async def callback(self, interaction: discord.Interaction):
        game = self.cog.active_game
        
        # Store the bet selection
        self.cog.active_bet = {
            "type": "total",
            "selection": self.values[0],
            "line": game["lines"]["total"]
        }
        
        # Ask for bet amount
        await interaction.response.send_message(
            f"Enter your bet amount for {self.values[0]} {game['lines']['total']}:",
            ephemeral=True
        )
        
        # Wait for amount input
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
            amount = int(float(msg.content))
            await self.process_bet(interaction, amount)
        except (asyncio.TimeoutError, ValueError):
            await interaction.followup.send("Invalid bet amount", ephemeral=True)

    async def process_bet(self, interaction: discord.Interaction, amount: int):
        user_id = self.cog.active_game["user_id"]
        game = self.cog.active_game
        bet = self.cog.active_bet
        
        # Simulate game outcome
        if game["sport"] == "NFL":
            team1_score = random.randint(10, 35)
            team2_score = random.randint(10, 35)
        else:
            team1_score = random.randint(90, 130)
            team2_score = random.randint(90, 130)
        
        total_score = team1_score + team2_score
        over_hit = total_score > bet["line"]
        
        # Calculate payout
        if (bet["selection"] == "over" and over_hit) or (bet["selection"] == "under" and not over_hit):
            payout = amount + (amount * (100/110))
            result_text = f"✅ Total {bet['selection']} {bet['line']}! Payout: ${payout:.2f}"
        else:
            payout = 0
            result_text = f"❌ Total {'under' if over_hit else 'over'} {bet['line']}. You lost ${amount}"
        
        # Update balance
        self.cog.balances[user_id] += payout - amount
        self.cog._save_balances()
        
        # Create result embed
        result_embed = discord.Embed(
            title=f"🎲 {game['teams']['team1']['name']} {team1_score}-{team2_score} {game['teams']['team2']['name']}",
            color=discord.Color.green() if payout > 0 else discord.Color.red()
        )
        result_embed.add_field(name="Result", value=result_text, inline=False)
        result_embed.add_field(name="New Balance", value=f"${self.cog.balances[user_id]:.2f}", inline=False)
        
        await interaction.followup.send(embed=result_embed)


async def setup(bot):
    await bot.add_cog(Games(bot))
    await bot.add_cog(SportsBetting(bot))