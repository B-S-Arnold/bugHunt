# from .base import Bug
# import random
# import re

# # Mapping of characters to neighboring keys (left and right neighbors for realistic typos)
# KEYBOARD_NEIGHBORS = {
#     'a': 'qs', 'b': 'vn', 'c': 'xv', 'd': 'sf', 'e': 'wr', 'f': 'dg',
#     'g': 'fh', 'h': 'gj', 'i': 'uo', 'j': 'hk', 'k': 'jl', 'l': 'k',
#     'm': 'n', 'n': 'bm', 'o': 'ip', 'p': 'o', 'q': 'wa', 'r': 'et',
#     's': 'ad', 't': 'ry', 'u': 'iy', 'v': 'cb', 'w': 'qe', 'x': 'zs',
#     'y': 'tu', 'z': 'as'
# }

# class TypoBug(Bug):
#     def inject(self, line: str) -> str:
#         words = line.split()
#         if not words:
#             return line

#         idx = random.randint(0, len(words) - 1)
#         word = words[idx]

#         if len(word) < 2 or word.startswith("#"):
#             return line

#         # Optional: Toggle to True to avoid typos on strings and numeric literals
#         if False:
#             if re.fullmatch(r"(\".*?\"|'.*?'|\d+)", word):
#                 return line

#         typo_type = random.choice(["swap", "omit", "duplicate", "replace", "insert"])
        
#         # swap mimics when keys are typed out of order 
#         if typo_type == "swap" and len(word) >= 2:
#             i = random.randint(0, len(word) - 2)
#             word = word[:i] + word[i+1] + word[i] + word[i+2:]

#         # omit mimics when keys are missed
#         elif typo_type == "omit":
#             i = random.randint(0, len(word) - 1)
#             word = word[:i] + word[i+1:]

#         # duplicate mimics when keys are (wrongly) struck more than once
#         elif typo_type == "duplicate":
#             i = random.randint(0, len(word) - 1)
#             word = word[:i] + word[i] + word[i:]

#         # replace mimics when a key neighboring the intended key is struck
#         elif typo_type == "replace":
#             i = random.randint(0, len(word) - 1)
#             c = word[i].lower()
#             if c in KEYBOARD_NEIGHBORS:
#                 replacement = random.choice(KEYBOARD_NEIGHBORS[c])
#                 word = word[:i] + replacement + word[i+1:]

#         # insert mimics when a random character is struck
#         elif typo_type == "insert":
#             i = random.randint(0, len(word))
#             char = random.choice("abcdefghijklmnopqrstuvwxyz")
#             word = word[:i] + char + word[i:]

#         words[idx] = word
#         return " ".join(words)
