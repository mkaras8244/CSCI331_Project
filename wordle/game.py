"""The Wordle game itself: one secret answer, a limited number of guesses."""

import random
from dataclasses import dataclass
from enum import Enum

from .feedback import ALL_GREEN, WORD_LENGTH, Feedback, Tile, score_guess
from .words import load_answers, load_valid_guesses

MAX_GUESSES = 6


class InvalidGuessError(ValueError):
    """Raised when a guess is rejected. The game state is left unchanged."""


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class GuessResult:
    word: str
    feedback: Feedback

    @property
    def is_correct(self) -> bool:
        return self.feedback == ALL_GREEN


class WordleGame:
    """A single game of Wordle.

    The answer is hidden behind `answer` only so that simulations can check it;
    a solver should rely solely on `history` (the guesses and their feedback).
    """

    def __init__(
        self,
        answer: str | None = None,
        *,
        max_guesses: int = MAX_GUESSES,
        answers: tuple[str, ...] | None = None,
        valid_guesses: frozenset[str] | None = None,
        rng: random.Random | None = None,
    ):
        self.answers = answers if answers is not None else load_answers()
        self.valid_guesses = valid_guesses if valid_guesses is not None else load_valid_guesses()
        self.max_guesses = max_guesses

        if answer is None:
            answer = (rng or random).choice(self.answers)
        answer = answer.lower()
        if len(answer) != WORD_LENGTH or not answer.isalpha():
            raise ValueError(f"answer must be a {WORD_LENGTH}-letter word: {answer!r}")
        self.answer = answer

        self.history: list[GuessResult] = []

    # ----- state -----

    @property
    def guesses_made(self) -> int:
        return len(self.history)

    @property
    def guesses_remaining(self) -> int:
        return self.guesses - len(self.history) 

    @property
    def status(self) -> GameStatus:
        if self.history and self.history[-1].is_correct:
            return GameStatus.WON
        if len(self.history) >= self.max_guesses:
            return GameStatus.LOST
        return GameStatus.IN_PROGRESS

    @property
    def is_over(self) -> bool:
        return self.status is not GameStatus.IN_PROGRESS

    @property
    def is_won(self) -> bool:
        return self.status is GameStatus.WON

    def letter_states(self) -> dict[str, Tile]:
        """Best-known color of each guessed letter, like the on-screen keyboard."""
        states: dict[str, Tile] = {}
        for result in self.history:
            for letter, tile in zip(result.word, result.feedback):
                states[letter] = max(tile, states.get(letter, Tile.GRAY))
        return states

    # ----- actions -----

    def validate(self, word: str) -> str | None:
        """Return why `word` would be rejected, or None if it is an acceptable guess."""
        if self.is_over:
            return "the game is already over"
        if len(word) != WORD_LENGTH:
            return f"guess must be {WORD_LENGTH} letters"
        if not word.isalpha():
            return "guess must contain only letters"
        if word not in self.valid_guesses:
            return "not in word list"
        return None

    def guess(self, word: str) -> GuessResult:
        """Submit a guess and return its feedback. Raises InvalidGuessError if rejected."""
        word = word.strip().lower()
        error = self.validate(word)
        if error:
            raise InvalidGuessError(error)

        result = GuessResult(word, score_guess(word, self.answer))
        self.history.append(result)
        return result


def _ordinal(n: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(n, f"{n}th")
