import random
import re
from .base import Bug

KEYBOARD_NEIGHBORS = {
    'a': 'qs', 'b': 'vn', 'c': 'xv', 'd': 'sf', 'e': 'wr', 'f': 'dg',
    'g': 'fh', 'h': 'gj', 'i': 'uo', 'j': 'hk', 'k': 'jl', 'l': 'k',
    'm': 'n', 'n': 'bm', 'o': 'ip', 'p': 'o', 'q': 'wa', 'r': 'et',
    's': 'ad', 't': 'ry', 'u': 'iy', 'v': 'cb', 'w': 'qe', 'x': 'zs',
    'y': 'tu', 'z': 'as'
}

class TypoBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        words = line.split()
        if not words:
            return line, None

        idx = random.randint(0, len(words) - 1)
        original_word = words[idx]

        if len(original_word) < 2 or original_word.startswith("#"):
            return line, None

        if False:
            if re.fullmatch(r"(\".*?\"|'.*?'|\d+)", original_word):
                return line, None

        typo_type = random.choice(["swap", "omit", "duplicate", "replace", "insert"])
        modified_word = original_word  # start as original

        if typo_type == "swap" and len(original_word) >= 2:
            i = random.randint(0, len(original_word) - 2)
            modified_word = (
                original_word[:i] +
                original_word[i+1] +
                original_word[i] +
                original_word[i+2:]
            )

        elif typo_type == "omit":
            i = random.randint(0, len(original_word) - 1)
            modified_word = original_word[:i] + original_word[i+1:]

        elif typo_type == "duplicate":
            i = random.randint(0, len(original_word) - 1)
            modified_word = original_word[:i] + original_word[i] + original_word[i:]

        elif typo_type == "replace":
            i = random.randint(0, len(original_word) - 1)
            c = original_word[i].lower()
            if c in KEYBOARD_NEIGHBORS:
                replacement = random.choice(KEYBOARD_NEIGHBORS[c])
                modified_word = original_word[:i] + replacement + original_word[i+1:]

        elif typo_type == "insert":
            i = random.randint(0, len(original_word))
            char = random.choice("abcdefghijklmnopqrstuvwxyz")
            modified_word = original_word[:i] + char + original_word[i:]

        if modified_word != original_word:
            words[idx] = modified_word
            return " ".join(words), {
                "bug_type": "typo",
                "typo_type": typo_type,
                "word_index": idx,
                "original_word": original_word,
                "modified_word": modified_word
            }
        else:
            return line, None