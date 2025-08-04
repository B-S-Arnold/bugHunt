import difflib
from .base_fixer import BaseFixer

class KeywordFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
        words = line.strip().split()
        if not words:
            return line
        first_word = words[0]
        if first_word not in self.known_words:
            close = difflib.get_close_matches(first_word, self.known_words, n=1, cutoff=0.7)
            if close:
                fixed = line.replace(first_word, close[0], 1)
                self.logs.append({
                    "line_number": line_number,
                    "original": line.strip(),
                    "fixed": fixed.strip(),
                    "fix_type": "keyword_typo"
                })
                return fixed
        return line
