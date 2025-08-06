import re
import keyword
import difflib
import ast
import sys
import pkgutil
import builtins

class BugFixer:
    def __init__(self):
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(builtins))
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
        line = self._fix_keyword_typos(line, line_number)  # <- Added here
        line = self._fix_unbalanced_symbols(line, line_number)
        line = self._fix_typos(line, line_number)
        line = self._fix_logic_bugs(line, line_number)
        line = self._fix_formatting(line, line_number)
        return line

    def _fix_keyword_typos(self, line: str, line_number: int) -> str:
        words = line.strip().split()
        if not words:
            return line
        first_word = words[0]
        if first_word not in self.keywords:
            close = difflib.get_close_matches(first_word, self.keywords, n=1, cutoff=0.7)
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

    def _fix_unbalanced_symbols(self, line: str, line_number: int) -> str:
        original = line
        pairs = {'(': ')', '[': ']', '{': '}'}
        open_stack = []

        for i, char in enumerate(line):
            if char in pairs:
                open_stack.append((char, i))
            elif char in pairs.values():
                if open_stack and pairs[open_stack[-1][0]] == char:
                    open_stack.pop()

        fixed = line
        for open_char, index in reversed(open_stack):
            close_char = pairs[open_char]

            if re.match(r'^\s*(def|if|for|while|with)\b', line) and not line.strip().endswith(':'):
                if not fixed.strip().endswith(close_char + ':'):
                    fixed = fixed.rstrip(':')
                    fixed += close_char + ':'
            else:
                fixed += close_char

        if fixed != original:
            self.logs.append({
                "line_number": line_number,
                "original": original.strip(),
                "fixed": fixed.strip(),
                "fix_type": "symbol_balance"
            })

        return fixed

    def _fix_typos(self, line: str, line_number: int) -> str:
        def replace_word(match):
            word = match.group()
            if word in self.known_words:
                return word
            close_matches = difflib.get_close_matches(word, self.known_words, n=1, cutoff=0.75)  # lower cutoff
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
