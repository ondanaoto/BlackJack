import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Suit(Enum):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4


@dataclass(frozen=True)
class Card:
    suit: Suit
    _value: int

    def __post_init__(self):
        if self._value < 1 or self._value > 13:
            raise ValueError("Invalid card value")

    @property
    def value(self) -> int:
        if self._value > 10:
            return 10
        return self._value


class DeckStatus(Enum):
    BLACKJACK = 1
    BURST = 2
    PLAYING = 3
    DETERMINED = 4


class Deck:
    def __init__(self, cards: list[Card], bet: int):
        self.cards: list[Card] = cards
        self.bet: int = bet
        self.status = DeckStatus.PLAYING

    def __len__(self):
        return len(self.cards)

    @property
    def total(self) -> list[int]:
        """Return possible total values of the deck."""
        total = 0
        ace_count = 0
        for card in self.cards:
            if card.value != 1:
                total += card.value
            else:
                ace_count += 1
        if ace_count == 0:
            if total + ace_count > 21:
                return []
            return [total]
        if total + ace_count + 10 <= 21:
            return [total + ace_count, total + ace_count + 10]
        if total + ace_count <= 21:
            return [total + ace_count]
        return []

    def _recompute_status_after_append(self) -> None:
        if self.total == []:
            self.status = DeckStatus.BURST
            return

        if len(self.cards) == 2 and self.total[-1] == 21:
            self.status = DeckStatus.BLACKJACK
            return

        self.status = DeckStatus.PLAYING

    def hit(self, card: Card) -> "Deck":
        if self.status != DeckStatus.PLAYING:
            raise RuntimeError("this deck can not play.")
        self.cards.append(card)
        self._recompute_status_after_append()
        return self

    def stand(self) -> "Deck":
        if self.status != DeckStatus.PLAYING:
            raise RuntimeError("this deck can not play.")
        self.status = DeckStatus.DETERMINED
        return self

    def double(self, card: Card) -> "Deck":
        if self.status != DeckStatus.PLAYING:
            raise RuntimeError("this deck can not play.")
        self.bet *= 2
        self.cards.append(card)
        self._recompute_status_after_append()
        if self.status == DeckStatus.PLAYING:
            self.stand()
        return self

    def split(self) -> tuple["Deck", "Deck"]:
        if not self.can_split():
            raise RuntimeError("cannot split")
        return Deck([self.cards[0]], self.bet), Deck([self.cards[1]], self.bet)

    def can_split(self) -> bool:
        if len(self) != 2:
            return False
        return self.cards[0].value == self.cards[1].value

    def can_double(self, already_split: bool) -> bool:
        if already_split:
            return len(self) == 1
        return len(self) == 2


class Yama:
    def __init__(self):
        self.__cards = [
            Card(suit, value) for suit in Suit for value in range(1, 14)
        ]
        self.shuffle()

    def pop(self) -> Card:
        card = self.__cards.pop()
        return card

    def shuffle(self):
        random.shuffle(self.__cards)


class PlayerAction(Enum):
    HIT = 1
    STAND = 2
    DOUBLE = 3
    SPLIT = 4


class HandKind(Enum):
    HARD = 1
    SOFT = 2
    PAIR = 3


class PlayerBoard:
    def __init__(self, fst: Card, snd: Card, bet: int):
        self.bet = bet
        self.deck: Deck = Deck([fst, snd], bet)
        self.split_deck: Deck = Deck([], 0)

    def split(self) -> None:
        if not self.deck.can_split():
            raise RuntimeError("cannot split")
        self.deck, self.split_deck = self.deck.split()

    def hit(self, card: Card) -> None:
        if not self.action_target:
            raise ValueError("cannot hit")
        self.action_target.hit(card)

    def stand(self) -> None:
        if not self.action_target:
            raise ValueError("cannot stand")
        self.action_target.stand()

    def double(self, card: Card) -> None:
        if not self.action_target:
            raise ValueError("cannot double")
        self.action_target.double(card)

    @property
    def action_target(self) -> Optional[Deck]:
        if self.deck.status == DeckStatus.PLAYING:
            return self.deck
        if not self.already_split():
            return None
        if self.split_deck.status == DeckStatus.PLAYING:
            return self.split_deck
        return None

    @property
    def action_range(self) -> list[PlayerAction]:
        if self.action_target is None:
            return []

        actions = [PlayerAction.HIT, PlayerAction.STAND]
        if self.action_target.can_double(self.already_split()):
            actions.append(PlayerAction.DOUBLE)
        if self._splittable():
            actions.append(PlayerAction.SPLIT)
        return actions

    @property
    def hand_kind(self) -> HandKind:
        if self._splittable():
            return HandKind.PAIR
        if len(self.deck.total) == 1:
            return HandKind.HARD
        if len(self.deck.total) == 2:
            return HandKind.SOFT
        raise RuntimeError("Unknown hand kind")

    @property
    def done(self) -> bool:
        return self.action_range == []

    def already_split(self) -> bool:
        return len(self.split_deck) > 0

    def _splittable(self) -> bool:
        return (not self.already_split()) and self.deck.can_split()


class DealerBoard:
    def __init__(self, fst: Card, snd: Card):
        self.deck: Deck = Deck([fst, snd], 0)

    def play(self, yama: Yama) -> Deck:
        while (
            self.deck.status == DeckStatus.PLAYING and self.deck.total[-1] < 17
        ):
            self.deck.hit(yama.pop())
        return self.deck

@dataclass(frozen=True)
class State:
    dealer_number: int
    hand_kind: HandKind
    player_total: list[int]


class BlackJackEnv:
    def reset(self, bet: int = 1) -> "BlackJackEnv":
        self.yama: Yama = Yama()
        self.player_board: PlayerBoard = PlayerBoard(
            self.yama.pop(), self.yama.pop(), bet
        )
        self.dealer_board: DealerBoard = DealerBoard(
            self.yama.pop(), self.yama.pop()
        )
        return self

    def __init__(self):
        self.reset()

    @property
    def state(self) -> Optional[State]:
        action_target = self.player_board.action_target
        if action_target is None:
            return None
        return State(
            dealer_number=self.dealer_board.deck.cards[0].value,
            hand_kind=self.player_board.hand_kind,
            player_total=action_target.total,
        )

    def step(self, action: PlayerAction) -> tuple[State, int, bool, dict]:
        if not self.action_range:
            raise RuntimeError("cannot step")
        if not (action in self.action_range):
            raise ValueError("Invalid action")

        if action == PlayerAction.HIT:
            self.player_board.hit(self.yama.pop())
        elif action == PlayerAction.STAND:
            self.player_board.stand()
        elif action == PlayerAction.DOUBLE:
            self.player_board.double(self.yama.pop())
        elif action == PlayerAction.SPLIT:
            self.player_board.split()

        if self.player_board.done:
            result = self._compare_result()
            return self.state, result, True, {}
        return self.state, 0, False, {}

    def render(self) -> None:
        print(f"Dealer: {self.dealer_board.deck.cards[0].value}")
        print(f"Player:")
        for card in self.player_board.deck.cards:
            print(card.value)
        if self.player_board.already_split():
            print(f"Player(split):")
            for card in self.player_board.split_deck.cards:
                print(card.value)
        print("Action range:")
        for i, action in enumerate(self.action_range):
            print(f"{i+1}: {action}")

    def _compare_result(self) -> int:
        dealer_deck = self.dealer_board.play(self.yama)
        reward = self._compare_deck(self.player_board.deck, dealer_deck)
        if self.player_board.already_split():
            reward += self._compare_deck(
                self.player_board.split_deck, dealer_deck
            )
        return reward

    @staticmethod
    def _compare_deck(player_deck: Deck, dealer_deck: Deck) -> int:
        bet = player_deck.bet
        if player_deck.status == DeckStatus.BURST:
            return -bet
        if player_deck.status == DeckStatus.BLACKJACK:
            if dealer_deck.status == DeckStatus.BLACKJACK:
                return 0
            return int(bet * 1.5)
        if dealer_deck.status == DeckStatus.BURST:
            return bet
        if dealer_deck.status == DeckStatus.BLACKJACK:
            return -bet
        player_total = player_deck.total[-1]
        dealer_total = dealer_deck.total[-1]
        if player_total > dealer_total:
            return bet
        if player_total < dealer_total:
            return -bet
        if player_total == dealer_total:
            return 0
        raise RuntimeError(
            f"""Unknown condition.
            dealer deck:{dealer_deck},
            player deck:{player_deck}"""
        )

    @property
    def action_range(self) -> list[PlayerAction]:
        return self.player_board.action_range


if __name__ == "__main__":
    env = BlackJackEnv()
    env.render()
    while True:
        action = int(input())
        print(PlayerAction(action))
        state, reward, done, _ = env.step(PlayerAction(action))
        env.render()
        if done:
            print("done")
            print(f"dealer_deck:")
            for card in env.dealer_board.deck.cards:
                print(card.value)
            print(f"dealer_total: {env.dealer_board.deck.total}")
            print(f"reward: {reward}")
            break
