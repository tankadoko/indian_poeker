from __future__ import annotations
from typing import List, Dict, Tuple
from enum import Enum
import matplotlib.pyplot as plt
import random


# Define card order
CardValue = str
# fmt: off
card_order: List[CardValue] = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
# fmt: on

WINNING_SCORE = 5
LOSE_FOLD_SCORE = -1
LOSE_CALL_SCORE = -2


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

    def tell_opponent_max(self, opponent: Player, opponents_list: List[Player]) -> bool:
        # the player tells the opponent if he has the max card, based on his honesty
        is_truely_max: bool = opponent.card.value == max(
            opponent.card.value for opponent in opponents_list
        )
        return self.tell_truth(is_truely_max)

    def make_decision(
        self, opponents: List["Player"], opponents_info: Dict[Player, bool]
    ):
        visible_max_card = max(opponent.card.value for opponent in opponents)
        # if the player thinks his card is >= max
        # he does not lie to himself
        if self.player_type == PlayerType.Random:
            return random.choice(["Call", "Fold"])

        # rational player
        # he caliculates the expected value of calling based on opponents evaluations
        # calc each opponent's evaluation * their honesty
        weighed_ave_possibility = self.calc_weighed_ave_possibility(opponents_info)
        expected_value = (
            weighed_ave_possibility * WINNING_SCORE
            + (1 - weighed_ave_possibility) * LOSE_CALL_SCORE
        )
        if expected_value > 0:
            return "Call"
        else:
            return "Fold"

    def calc_weighed_ave_possibility(self, opponents_info: Dict[Player, bool]):
        expected_value = 0
        for opponent, is_max in opponents_info.items():
            expected_value += is_max * opponent.honesty
        expected_value /= len(opponents_info)
        return expected_value


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

        # Players tell opponents if they have the max card
        # this info means evaluations from others to each player
        opponents_info = {player: {} for player in self.players}
        for player in self.players:
            opponents_list: List[Player] = [p for p in self.players if p != player]
            for opponent in opponents_list:
                opponents_info[opponent][player] = player.tell_opponent_max(
                    opponent, opponents_list
                )

        # Players make their decision
        decisions = {
            player: player.make_decision(
                [p for p in self.players if p != player], opponents_info[player]
            )
            for player in self.players
        }

        # calc scores
        max_value = max(
            player.card.value for player in self.players if decisions[player] == "Call"
        )
        for player, decision in decisions.items():
            print("a", player.score)
            if decision == "Fold":
                player.score -= LOSE_FOLD_SCORE
            elif decision == "Call":
                if player.card.value == max_value:
                    player.score += WINNING_SCORE
                else:
                    player.score -= LOSE_CALL_SCORE
            print("b", player.score)

    def play_game(self, num_rounds: int):
        for _ in range(num_rounds):
            self.play_round()

    def get_scores(self) -> Dict[Player, int]:
        return {player: player.score for player in self.players}


def game(peoples: int, rounds: int):
    game = IndianPokerGame(peoples)
    game.play_game(rounds)
    return game.get_scores()


# visualize the result using matplotlib
# show relationship between decision making(rational or random) and score
def visualize(scores: Dict[Player, int]):
    rational_scores = []
    random_scores = []
    for player, score in scores.items():
        print(f"player honesty: {player.honesty}, score: {score}")
        if player.player_type == PlayerType.Rational:
            rational_scores.append(score)
        else:
            random_scores.append(score)
    plt.plot(rational_scores, label="rational")
    plt.plot(random_scores, label="random")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    scores = game(40, 1)
    visualize(scores)
