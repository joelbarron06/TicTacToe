import random
import json
import os
from datetime import datetime

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = self.get_value()
    
    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Aces handled dynamically
        else:
            return int(self.rank)
    
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def ascii_art(self):
        """Generate ASCII art for the card"""
        suit_symbols = {'♠': '♠', '♥': '♥', '♦': '♦', '♣': '♣'}
        
        lines = [
            "┌─────────┐",
            f"│{self.rank:<2}       │",
            "│         │",
            f"│    {suit_symbols[self.suit]}    │",
            "│         │",
            f"│       {self.rank:>2}│",
            "└─────────┘"
        ]
        return lines

class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.shuffle_point = 0.75  # Reshuffle when 75% of cards are used
        self.reset_deck()
    
    def reset_deck(self):
        """Create a fresh deck with multiple decks"""
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        self.cards = []
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(suit, rank))
        
        self.shuffle()
    
    def shuffle(self):
        """Realistic casino shuffling - multiple passes"""
        # Riffle shuffle multiple times
        for _ in range(7):  # 7 shuffles for good randomization
            self.riffle_shuffle()
        
        # Cut the deck
        cut_point = random.randint(len(self.cards) // 4, 3 * len(self.cards) // 4)
        self.cards = self.cards[cut_point:] + self.cards[:cut_point]
    
    def riffle_shuffle(self):
        """Simulate riffle shuffle"""
        mid = len(self.cards) // 2
        left = self.cards[:mid]
        right = self.cards[mid:]
        
        shuffled = []
        while left and right:
            # Randomly choose from left or right pile
            if random.random() < 0.5:
                shuffled.append(left.pop(0))
            else:
                shuffled.append(right.pop(0))
        
        # Add remaining cards
        shuffled.extend(left)
        shuffled.extend(right)
        
        self.cards = shuffled
    
    def deal_card(self):
        """Deal a card and check if reshuffle is needed"""
        if len(self.cards) < (self.num_decks * 52 * (1 - self.shuffle_point)):
            print("\n🔄 Shuffling deck...")
            self.reset_deck()
        
        return self.cards.pop()
    
    def cards_remaining(self):
        return len(self.cards)

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0
    
    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()
    
    def adjust_for_ace(self):
        """Adjust hand value for aces"""
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.value == 21
    
    def is_bust(self):
        return self.value > 21
    
    def display_hand(self, hide_first=False):
        """Display hand with ASCII art"""
        if not self.cards:
            return
        
        # Create card art lines
        all_lines = []
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                # Hidden card
                lines = [
                    "┌─────────┐",
                    "│░░░░░░░░░│",
                    "│░░░░░░░░░│",
                    "│░░░░░░░░░│",
                    "│░░░░░░░░░│",
                    "│░░░░░░░░░│",
                    "└─────────┘"
                ]
            else:
                lines = card.ascii_art()
            all_lines.append(lines)
        
        # Print cards side by side
        for row in range(7):
            line = ""
            for card_lines in all_lines:
                line += card_lines[row] + "  "
            print(line)
        
        # Show value
        if not hide_first:
            print(f"Value: {self.value}")
        else:
            visible_value = sum(card.value for card in self.cards[1:])
            print(f"Visible value: {visible_value}")

class User:
    def __init__(self, username):
        self.username = username
        self.balance = 0
        self.total_deposited = 0
        self.total_bet = 0
        self.total_won = 0
        self.games_played = 0
        self.games_won = 0
        self.created_date = datetime.now().isoformat()
    
    def deposit(self, amount):
        self.balance += amount
        self.total_deposited += amount
    
    def place_bet(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.total_bet += amount
            return True
        return False
    
    def win_bet(self, amount):
        self.balance += amount
        self.total_won += amount
        self.games_won += 1
    
    def get_net_earnings(self):
        return self.total_won - self.total_bet
    
    def get_roi(self):
        if self.total_bet == 0:
            return 0
        return ((self.total_won - self.total_bet) / self.total_bet) * 100
    
    def get_win_rate(self):
        if self.games_played == 0:
            return 0
        return (self.games_won / self.games_played) * 100

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.current_user = None
        self.users_file = "blackjack_users.json"
        self.load_users()
    
    def load_users(self):
        """Load user data from file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self.users = {}
                    for username, user_data in data.items():
                        user = User(username)
                        user.__dict__.update(user_data)
                        self.users[username] = user
            else:
                self.users = {}
        except:
            self.users = {}
    
    def save_users(self):
        """Save user data to file"""
        try:
            data = {}
            for username, user in self.users.items():
                data[username] = user.__dict__
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def login(self):
        """Handle user login/registration"""
        print("🎰 Welcome to Blackjack Casino! 🎰")
        print("=" * 40)
        
        username = input("Enter username: ").strip()
        
        if username in self.users:
            self.current_user = self.users[username]
            print(f"\nWelcome back, {username}!")
        else:
            print(f"\nCreating new account for {username}")
            self.current_user = User(username)
            self.users[username] = self.current_user
            print("Account created successfully!")
        
        self.show_user_stats()
    
    def show_user_stats(self):
        """Display user statistics"""
        user = self.current_user
        print("\n" + "=" * 50)
        print(f"📊 {user.username}'s Statistics")
        print("=" * 50)
        print(f"💰 Current Balance: ${user.balance:.2f}")
        print(f"📥 Total Deposited: ${user.total_deposited:.2f}")
        print(f"🎯 Total Bet: ${user.total_bet:.2f}")
        print(f"🏆 Total Won: ${user.total_won:.2f}")
        print(f"📈 Net Earnings: ${user.get_net_earnings():.2f}")
        print(f"📊 ROI: {user.get_roi():.2f}%")
        print(f"🎮 Games Played: {user.games_played}")
        print(f"🏅 Win Rate: {user.get_win_rate():.1f}%")
        print("=" * 50)
    
    def handle_deposit(self):
        """Handle user deposits"""
        while True:
            try:
                amount = float(input("\nEnter deposit amount (or 0 to skip): $"))
                if amount == 0:
                    break
                elif amount > 0:
                    self.current_user.deposit(amount)
                    print(f"✅ Deposited ${amount:.2f}. New balance: ${self.current_user.balance:.2f}")
                    break
                else:
                    print("❌ Amount must be positive!")
            except ValueError:
                print("❌ Please enter a valid number!")
    
    def get_bet_amount(self):
        """Get bet amount from user"""
        while True:
            try:
                print(f"\nCurrent balance: ${self.current_user.balance:.2f}")
                bet = float(input("Enter bet amount: $"))
                
                if bet <= 0:
                    print("❌ Bet must be positive!")
                elif bet > self.current_user.balance:
                    print("❌ Insufficient funds!")
                else:
                    return bet
            except ValueError:
                print("❌ Please enter a valid number!")
    
    def deal_initial_cards(self):
        """Deal initial two cards to player and dealer"""
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        
        # Deal two cards each
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal_card())
            self.dealer_hand.add_card(self.deck.deal_card())
    
    def player_turn(self):
        """Handle player's turn"""
        while True:
            print("\n" + "="*50)
            print("Your hand:")
            self.player_hand.display_hand()
            
            print("\nDealer's hand:")
            self.dealer_hand.display_hand(hide_first=True)
            
            if self.player_hand.is_bust():
                print("\n💥 BUST! You lose!")
                return False
            
            if self.player_hand.value == 21:
                print("\n🎯 21! Standing...")
                return True
            
            print(f"\nCards remaining in deck: {self.deck.cards_remaining()}")
            choice = input("\n(H)it or (S)tand? ").lower().strip()
            
            if choice == 'h':
                self.player_hand.add_card(self.deck.deal_card())
            elif choice == 's':
                return True
            else:
                print("❌ Please enter 'h' for hit or 's' for stand")
    
    def dealer_turn(self):
        """Handle dealer's turn"""
        print("\n" + "="*50)
        print("Dealer reveals cards:")
        self.dealer_hand.display_hand()
        
        while self.dealer_hand.value < 17:
            print("\nDealer hits...")
            input("Press Enter to continue...")
            self.dealer_hand.add_card(self.deck.deal_card())
            self.dealer_hand.display_hand()
        
        if self.dealer_hand.is_bust():
            print("\n💥 Dealer busts!")
        else:
            print(f"\nDealer stands with {self.dealer_hand.value}")
    
    def determine_winner(self, bet_amount):
        """Determine winner and handle payouts"""
        player_val = self.player_hand.value
        dealer_val = self.dealer_hand.value
        
        print("\n" + "="*50)
        print("FINAL RESULTS")
        print("="*50)
        
        # Player bust
        if self.player_hand.is_bust():
            print("💔 You busted! Dealer wins!")
            return 0
        
        # Dealer bust
        if self.dealer_hand.is_bust():
            print("🎉 Dealer busted! You win!")
            payout = bet_amount * 2
            self.current_user.win_bet(payout)
            return payout
        
        # Blackjack checks
        player_bj = self.player_hand.is_blackjack()
        dealer_bj = self.dealer_hand.is_blackjack()
        
        if player_bj and dealer_bj:
            print("🤝 Both have blackjack! Push!")
            self.current_user.balance += bet_amount  # Return bet
            return bet_amount
        elif player_bj:
            print("🎰 BLACKJACK! You win!")
            payout = bet_amount * 2.5  # 3:2 payout
            self.current_user.win_bet(payout)
            return payout
        elif dealer_bj:
            print("💔 Dealer has blackjack! You lose!")
            return 0
        
        # Regular comparison
        if player_val > dealer_val:
            print("🎉 You win!")
            payout = bet_amount * 2
            self.current_user.win_bet(payout)
            return payout
        elif player_val < dealer_val:
            print("💔 Dealer wins!")
            return 0
        else:
            print("🤝 Push! It's a tie!")
            self.current_user.balance += bet_amount  # Return bet
            return bet_amount
    
    def play_round(self):
        """Play a single round of blackjack"""
        # Check if user has funds
        if self.current_user.balance <= 0:
            print("\n💸 You're out of money! Please deposit to continue.")
            self.handle_deposit()
            if self.current_user.balance <= 0:
                return False
        
        # Get bet
        bet_amount = self.get_bet_amount()
        if not self.current_user.place_bet(bet_amount):
            print("❌ Unable to place bet!")
            return True
        
        # Update games played
        self.current_user.games_played += 1
        
        # Deal cards
        self.deal_initial_cards()
        
        # Check for immediate blackjack
        if self.player_hand.is_blackjack():
            print("\n🎰 BLACKJACK!")
            self.player_hand.display_hand()
            print("\nDealer's hand:")
            self.dealer_hand.display_hand()
            
            payout = self.determine_winner(bet_amount)
            print(f"\nPayout: ${payout:.2f}")
        else:
            # Player turn
            if self.player_turn():
                # Dealer turn
                self.dealer_turn()
            
            # Determine winner
            payout = self.determine_winner(bet_amount)
            print(f"Payout: ${payout:.2f}")
        
        print(f"New balance: ${self.current_user.balance:.2f}")
        self.save_users()
        return True
    
    def main_menu(self):
        """Main game menu"""
        while True:
            print("\n" + "="*50)
            print("🎰 BLACKJACK CASINO")
            print("="*50)
            print("1. Play Blackjack")
            print("2. View Statistics")
            print("3. Deposit Money")
            print("4. Logout")
            print("5. Quit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                if not self.play_round():
                    break
            elif choice == '2':
                self.show_user_stats()
            elif choice == '3':
                self.handle_deposit()
            elif choice == '4':
                self.current_user = None
                self.login()
            elif choice == '5':
                print("\n👋 Thanks for playing! Goodbye!")
                break
            else:
                print("❌ Invalid option! Please select 1-5.")
    
    def run(self):
        """Run the game"""
        try:
            self.login()
            if self.current_user.balance == 0:
                self.handle_deposit()
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Game interrupted. Your progress has been saved!")
        finally:
            self.save_users()

# Run the game
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()