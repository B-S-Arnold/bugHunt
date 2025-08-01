import re
import keyword
import difflib
import ast
import sys
import pkgutil

class BugFixer:
    def __init__(self):
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(__builtins__))
        self.stdlib_modules = set(name for _, name, _ in pkgutil.iter_modules())
        self.known_words = set()
        self.logs = []

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
            pass

        return user_symbols

    def update_known_words(self, code: str):
        user_defined = self.extract_user_symbols(code)
        self.known_words = self.keywords | self.builtins | self.stdlib_modules | user_defined


    def fix_line(self, line: str, line_number: int) -> str:
        original = line
        line = self._fix_typos(line, line_number)
        line = self._fix_logic_bugs(line, line_number)
        line = self._fix_formatting(line, line_number)
        return line

    def _fix_typos(self, line: str, line_number: int) -> str:
        def replace_word(match):
            word = match.group()
            if word in self.known_words:
                return word
            close_matches = difflib.get_close_matches(word, self.known_words, n=1, cutoff=0.85)
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

    def _fix_logic_bugs(self, line: str, line_number: int) -> str:
        original = line
        fixes = [
            (r'!=', '=='),
            (r'>=', '<='),
            (r'<=', '>='),
            (r'\bTrue\b', 'False'),
            (r'\bFalse\b', 'True'),
            (r'range\(([^)]+)\s*\+\s*1\)', r'range(\1)')
        ]
        for pattern, replacement in fixes:
            if re.search(pattern, line):
                fixed_line = re.sub(pattern, replacement, line)
                self.logs.append({
                    "line_number": line_number,
                    "original": line.strip(),
                    "fixed": fixed_line.strip(),
                    "fix_type": "logic_bug_fix"
                })
                line = fixed_line
        return line

    def _fix_formatting(self, line: str, line_number: int) -> str:
        original = line
        fixed = re.sub(r'\s*([=+\-*/<>])\s*', r' \1 ', line)
        fixed = re.sub(r'\s*,\s*', ', ', fixed)
        fixed = re.sub(r'\s*:\s*', ': ', fixed)
        if fixed != original:
            self.logs.append({
                "line_number": line_number,
                "original": original.strip(),
                "fixed": fixed.strip(),
                "fix_type": "formatting"
            })
        return fixed

    def fix_code(self, code: str) -> tuple[str, list[dict]]:
        self.logs = []
        self.update_known_words(code)
        lines = code.splitlines()
        fixed_lines = []
        for i, line in enumerate(lines):
            fixed_lines.append(self.fix_line(line, i + 1))
        return "\n".join(fixed_lines), self.logs
