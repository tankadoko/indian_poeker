from typing import List, Dict, Tuple
from enum import Enum
import random


# Define card order
CardValue = str
# fmt: off
card_order: List[CardValue] = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
# fmt: on


class Card:
    def __init__(self, value: CardValue):
        self.value = value


class PlayerType(Enum):
    Rational = 0
    Random = 1


class Player:
    def __init__(self, honesty: float, isRational: bool):
        self.honesty = honesty
        self.card: Card = Card("2")  # weakest card as default
        self.player_type = PlayerType.Rational if isRational else PlayerType.Random
        self.score: int = 0

    def tell_truth(self, maximum: bool) -> bool:
        if random.random() < self.honesty:  # tell truth
            return maximum
        else:
            return not maximum

    def make_decision(self, opponents: List["Player"]) -> str:
        visible_max_card = max(opponent.card.value for opponent in opponents)
        # if the player thinks his card is >= max
        # he does not lie to himself
        if self.player_type == PlayerType.Rational:
            # Rational player makes a decision based on expected value
            if self.card.value >= visible_max_card:
                return "Call"
            else:
                return "Fold"
        else:
            # Random player makes a decision randomly
            return random.choice(["Call", "Fold"])


class Deck:
    def __init__(self):
        ENOUGH_NUMBER = 10**5
        self.cards = [Card(value) for value in card_order * ENOUGH_NUMBER]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()


class IndianPokerGame:
    def __init__(self, num_players: int):
        # set honesty randomly
        self.players: List[Player] = [
            Player(random.random(), i % 2 == 0) for i in range(num_players)
        ]
        self.deck = Deck()

    def play_round(self):
        self.deck.shuffle()
        for player in self.players:
            player.card = self.deck.draw()

        # players make their decision
        decisions = {
            player: player.make_decision([p for p in self.players if p != player])
            for player in self.players
        }

        # calc scores
        max_value = max(
            player.card.value for player in self.players if decisions[player] == "Call"
        )
        for player, decision in decisions.items():
            if decision == "Fold":
                player.score -= 1
            elif decision == "Call":
                if player.card.value == max_value:
                    player.score += 5
                else:
                    player.score -= 2

    def play_game(self, num_rounds: int):
        for _ in range(num_rounds):
            self.play_round()

    def get_scores(self) -> Dict[Player, int]:
        return {player: player.score for player in self.players}


# 5人で100ラウンドを行う
game_with_5 = IndianPokerGame(5)
game_with_5.play_game(100)
scores_with_5 = game_with_5.get_scores()

# 100人で100ラウンドを行う
game_with_100 = IndianPokerGame(100)
game_with_100.play_game(100)
scores_with_100 = game_with_100.get_scores()

# 結果の表示
print("Scores for 5-player game:", scores_with_5)
print("Scores for 100-player game:", scores_with_100)
