"""A Python remake of Wordle, built as the environment for AI solver agents."""

from .feedback import ( 
    ALL_GREEN,
    WORD_LENGTH,
    Feedback,
    Tile,
    feedback_from_int,
    feedback_from_string,
    feedback_to_int,
    feedback_to_string,
    score_guess,
)
from .game import MAX_GUESSES, GameStatus, GuessResult, InvalidGuessError, WordleGame
from .words import load_answers, load_valid_guesses

__all__ = [
    "ALL_GREEN", "WORD_LENGTH", "MAX_GUESSES",
    "Feedback", "Tile", "GameStatus", "GuessResult", "InvalidGuessError", "WordleGame",
    "score_guess", "feedback_to_int", "feedback_from_int",
    "feedback_to_string", "feedback_from_string",
    "load_answers", "load_valid_guesses",
]
