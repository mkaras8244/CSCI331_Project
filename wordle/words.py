"""Loading the answer list and the list of valid guesses."""

from functools import lru_cache 
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ANSWERS_FILE = DATA_DIR / "answers.txt"          # cfreshman: 2,315 possible solutions
VALID_WORDS_FILE = DATA_DIR / "valid_words.txt"  # dracos: 14,855 allowed guesses


def _load(path: Path) -> tuple[str, ...]:
    words = (line.strip().lower() for line in path.read_text().splitlines())
    return tuple(sorted({w for w in words if len(w) == 5 and w.isalpha()}))


@lru_cache(maxsize=None)
def load_answers() -> tuple[str, ...]:
    """Every word that can be the solution, sorted alphabetically."""
    return _load(ANSWERS_FILE)


@lru_cache(maxsize=None)
def load_valid_guesses() -> frozenset[str]:
    """Every word accepted as a guess (always includes all answers)."""
    return frozenset(_load(VALID_WORDS_FILE)) | frozenset(load_answers())
