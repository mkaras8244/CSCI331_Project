"""Tile feedback scoring, matching the official Wordle rules for repeated letters."""

from enum import IntEnum

WORD_LENGTH = 5


class Tile(IntEnum):
    GRAY = 0    # letter is not in the answer (or all copies are already accounted for)
    YELLOW = 1  # letter is in the answer, but in a different position
    GREEN = 2   # letter is in the answer at this exact position


Feedback = tuple[Tile, ...]

ALL_GREEN: Feedback = (Tile.GREEN,) * WORD_LENGTH


def score_guess(guess: str, answer: str) -> Feedback:
    """Return the tile colors Wordle would show for `guess` against `answer`.

    Greens are assigned first. Remaining letters are then marked yellow left to
    right, but only while unmatched copies of that letter remain in the answer.
    e.g. score_guess("speed", "abide") -> (GRAY, GRAY, YELLOW, GRAY, YELLOW)
    """
    if len(guess) != len(answer):
        raise ValueError("guess and answer must be the same length")

    tiles = [Tile.GRAY] * len(guess)
    unmatched: dict[str, int] = {}

    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            tiles[i] = Tile.GREEN
        else:
            unmatched[a] = unmatched.get(a, 0) + 1

    for i, g in enumerate(guess):
        if tiles[i] != Tile.GREEN and unmatched.get(g, 0) > 0:
            tiles[i] = Tile.YELLOW
            unmatched[g] -= 1

    return tuple(tiles) 


def feedback_to_int(feedback: Feedback) -> int:
    """Encode feedback as a base-3 integer in [0, 243), handy for bucketing words."""
    value = 0
    for tile in feedback:
        value = value * 3 + int(tile)
    return value


def feedback_from_int(value: int, length: int = WORD_LENGTH) -> Feedback:
    """Inverse of feedback_to_int."""
    tiles = []
    for _ in range(length):
        value, digit = divmod(value, 3)
        tiles.append(Tile(digit))
    return tuple(reversed(tiles))


def feedback_to_string(feedback: Feedback) -> str:
    """Compact text form, e.g. 'GY--G' (G = green, Y = yellow, - = gray)."""
    return "".join({Tile.GREEN: "G", Tile.YELLOW: "Y", Tile.GRAY: "-"}[t] for t in feedback)


def feedback_from_string(text: str) -> Feedback:
    """Parse the compact text form produced by feedback_to_string.

    Also accepts 'B'/'X'/'.'/'0' for gray, '1' for yellow and '2' for green.
    """
    mapping = {"G": Tile.GREEN, "2": Tile.GREEN, "Y": Tile.YELLOW, "1": Tile.YELLOW,
               "-": Tile.GRAY, "B": Tile.GRAY, "X": Tile.GRAY, ".": Tile.GRAY, "0": Tile.GRAY}
    try:
        return tuple(mapping[c] for c in text.strip().upper())
    except KeyError as e:
        raise ValueError(f"invalid feedback character: {e.args[0]!r}") from None
