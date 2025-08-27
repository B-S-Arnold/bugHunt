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

        self.pre_fixers = [
            KeywordFixer(),
            SymbolFixer(),
            TypoFixer(),
            LogicFixer(),
            FormatFixer(),
        ]

        self.indent_fixer = IndentFixer()

    def extract_user_symbols(self, code: str) -> set[str]:
        """Collects function names, class names, variables, and attributes from code."""
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
                elif isinstance(node, ast.Attribute):
                    user_symbols.add(node.attr)
        except SyntaxError:
            pass
        return user_symbols

    def update_known_words(self, code: str):
        """Refresh the dictionary of known words for typo fixing."""
        user_defined = self.extract_user_symbols(code)
        self.known_words = self.keywords | self.builtins | self.stdlib_modules | user_defined

    def fix_code(self, code: str) -> tuple[str, list[dict]]:
        self.logs = []

        self.update_known_words(code)

        safe_words = ["path", "strftime"]
        self.known_words.update(safe_words)

        # --- First batch (high-level corrections)
        for fixer in [KeywordFixer(), LogicFixer()]:
            fixer.set_context(self.known_words, self.logs)
            if hasattr(fixer, "fix_code"):
                code = fixer.fix_code(code)
            else:
                lines = code.splitlines()
                lines = [fixer.fix_line(line, i + 1) for i, line in enumerate(lines)]
                code = "\n".join(lines)

        self.update_known_words(code)
        self.known_words.update(safe_words)

        # --- Second batch (typos, symbols, first format pass)
        for fixer in [TypoFixer(), SymbolFixer()]:
            fixer.set_context(self.known_words, self.logs)
            if hasattr(fixer, "fix_code"):
                code = fixer.fix_code(code)
            else:
                lines = code.splitlines()
                lines = [fixer.fix_line(line, i + 1) for i, line in enumerate(lines)]
                code = "\n".join(lines)

        # --- Indentation fixer (still useful after manual formatting)
        self.indent_fixer.set_context(self.known_words, self.logs)
        code = self.indent_fixer.fix_code(code)

        # --- Final AST reformat pass (best chance for perfect output)
        final_formatter = FormatFixer()
        final_formatter.set_context(self.known_words, self.logs)
        code = final_formatter.fix_code(code)

        return code, self.logs
