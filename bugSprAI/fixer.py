import re
import keyword
import difflib
import ast

class BugFixer:
    def __init__(self):
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(__builtins__))
        self.known_words = set()

    def extract_user_symbols(self, code: str) -> set[str]:
        user_symbols = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    user_symbols.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    user_symbols.add(node.name)
                elif isinstance(node, ast.arg):
                    user_symbols.add(node.arg)
                elif isinstance(node, ast.Name):
                    user_symbols.add(node.id)
        except SyntaxError:
            pass  # fallback if broken code

        return user_symbols

    def update_known_words(self, code: str):
        user_defined = self.extract_user_symbols(code)
        self.known_words = self.keywords | self.builtins | user_defined

    def fix_line(self, line: str) -> str:
        line = self._fix_typos(line)
        line = self._fix_logic_bugs(line)
        line = self._fix_formatting(line)
        return line

    def _fix_typos(self, line: str) -> str:
        def replace_word(match):
            word = match.group()
            if word in self.known_words:
                return word
            close_matches = difflib.get_close_matches(word, self.known_words, n=1, cutoff=0.85)
            return close_matches[0] if close_matches else word

        return re.sub(r'\b\w+\b', replace_word, line)

    def _fix_logic_bugs(self, line: str) -> str:
        line = re.sub(r'!=', '==', line)
        line = re.sub(r'>=', '<=', line)
        line = re.sub(r'<=', '>=', line)
        line = re.sub(r'\bTrue\b', 'False', line)
        line = re.sub(r'\bFalse\b', 'True', line)
        line = re.sub(r'range\(([^)]+)\s*\+\s*1\)', r'range(\1)', line)
        return line

    def _fix_formatting(self, line: str) -> str:
        line = re.sub(r'\s*([=+\-*/<>])\s*', r' \1 ', line)
        line = re.sub(r'\s*,\s*', ', ', line)
        line = re.sub(r'\s*:\s*', ': ', line)
        return line

    def fix_code(self, code: str) -> str:
        self.update_known_words(code)
        lines = code.splitlines()
        fixed_lines = [self.fix_line(line) for line in lines]
        return "\n".join(fixed_lines)
