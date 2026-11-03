"""Text interface for playing Wordle in the terminal."""

import argparse
import os
import random
import sys

from .feedback import Feedback, Tile, feedback_to_string
from .game import InvalidGuessError, WordleGame

KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_TILE_STYLE = {
    Tile.GREEN: "\033[1;30;42m",   # black on green
    Tile.YELLOW: "\033[1;30;43m",  # black on yellow
    Tile.GRAY: "\033[1;37;100m",   # white on dark gray
}
_UNUSED_STYLE = "\033[1;30;47m"    # black on light gray
_RESET = "\033[0m"


def render_row(word: str, feedback: Feedback) -> str: 
    if not _USE_COLOR:
        return f"{word.upper()}  {feedback_to_string(feedback)}"
    return "".join(f"{_TILE_STYLE[t]} {c.upper()} {_RESET}" for c, t in zip(word, feedback))


def render_keyboard(states: dict[str, Tile]) -> str:
    lines = []
    for indent, row in enumerate(KEYBOARD_ROWS):
        keys = []
        for c in row:
            if _USE_COLOR:
                style = _TILE_STYLE[states[c]] if c in states else _UNUSED_STYLE
                keys.append(f"{style} {c.upper()} {_RESET}")
            else:
                mark = {Tile.GREEN: "+", Tile.YELLOW: "?", Tile.GRAY: "_"}.get(states.get(c), " ")
                keys.append(f"{c.upper()}{mark}")
        lines.append(" " * indent + " ".join(keys))
    return "\n".join(lines)


def render_board(game: WordleGame) -> str:
    rows = [render_row(r.word, r.feedback) for r in game.history]
    empty = "".join(f"{_UNUSED_STYLE}   {_RESET}" for _ in range(5)) if _USE_COLOR else "_____"
    rows += [empty] * game.guesses_remaining
    return "\n".join(rows)


def play(game: WordleGame) -> bool:
    """Run one interactive game. Returns True if the player won."""
    print(f"Guess the 5-letter word in {game.max_guesses} tries.")
    if not _USE_COLOR:
        print("Feedback key: G = right spot, Y = wrong spot, - = not in word")

    while not game.is_over:
        print()
        print(render_board(game))
        print()
        print(render_keyboard(game.letter_states()))
        try:
            word = input(f"\nGuess {game.guesses_made + 1}/{game.max_guesses}: ")
        except (EOFError, KeyboardInterrupt):
            print(f"\nQuitting. The word was {game.answer.upper()}.")
            return False
        try:
            game.guess(word)
        except InvalidGuessError as e:
            print(f"  ! {e}")

    print()
    print(render_board(game))
    if game.is_won:
        print(f"\nSolved in {game.guesses_made}/{game.max_guesses}!")
    else:
        print(f"\nOut of guesses. The word was {game.answer.upper()}.")
    return game.is_won


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Play Wordle in the terminal.")
    parser.add_argument("--answer", help="set the secret word (for testing)")
    parser.add_argument("--max-guesses", type=int, default=6)
    parser.add_argument("--seed", type=int, help="random seed for picking the answer")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    while True:
        game = WordleGame(args.answer, max_guesses=args.max_guesses, rng=rng)
        play(game)
        if args.answer:
            break
        try:
            again = input("\nPlay again? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if again not in ("y", "yes"):
            break


if __name__ == "__main__":
    main()
