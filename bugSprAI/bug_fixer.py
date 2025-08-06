import re
import keyword
import ast
import pkgutil
import builtins
from fixers import *

class BugFixer:
    def __init__(self):
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(builtins))
        self.stdlib_modules = set(name for _, name, _ in pkgutil.iter_modules())
        self.known_words = set()
        self.logs = []

        self.fixers = [
            KeywordFixer(),
            SymbolFixer(),
            TypoFixer(),
            LogicFixer(),
            FormatFixer()
        ]

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
        for fixer in self.fixers:
            fixer.set_context(self.known_words, self.logs)
            line = fixer.fix_line(line, line_number)
        return line

    def fix_code(self, code: str) -> tuple[str, list[dict]]:
        self.logs = []
        self.update_known_words(code)
        lines = code.splitlines()
        fixed_lines = []
        for i, line in enumerate(lines):
            fixed_lines.append(self.fix_line(line, i + 1))
        return "\n".join(fixed_lines), self.logs
