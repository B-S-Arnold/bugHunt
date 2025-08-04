import re
import difflib
from .base_fixer import BaseFixer

class TypoFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
        def replace_word(match):
            word = match.group()
            if word in self.known_words:
                return word
            close_matches = difflib.get_close_matches(word, self.known_words, n=1, cutoff=0.75)
            if close_matches:
                self.logs.append({
                    "line_number": line_number,
                    "original": word,
                    "fixed": close_matches[0],
                    "fix_type": "typo_correction"
                })
                return close_matches[0]
            return word

        return re.sub(r'\b\w+\b', replace_word, line)
