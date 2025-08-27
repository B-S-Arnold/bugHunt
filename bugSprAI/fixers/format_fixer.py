import ast
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.used_ast = False

    def fix_code(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            self.used_ast = True
            return ast.unparse(tree)
        except SyntaxError:
            self.used_ast = False
            return self.fallback_format(code)

    def fallback_format(self, code: str) -> str:
        fixed_lines = []
        scope_stack = []

        lines = code.splitlines()

        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                fixed_lines.append("")
                continue

            leading_spaces = len(line) - len(stripped)

            while scope_stack and leading_spaces < scope_stack[-1][1]:
                scope_stack.pop()

            block_openers = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
            block_followups = ('elif', 'else', 'except', 'finally')

            first_word = stripped.split()[0]

            if first_word in block_followups:
                if scope_stack:
                    indent = scope_stack[-1][1]
                else:
                    indent = 0
                if not stripped.endswith(':'):
                    stripped += ':'
                scope_stack.append((first_word, indent, indent + 4))
                fixed_lines.append(' ' * indent + stripped)
                continue

            if first_word in block_openers:
                indent = leading_spaces
                if not stripped.endswith(':'):
                    stripped += ':'
                scope_stack.append((first_word, indent, indent + 4))
                fixed_lines.append(' ' * indent + stripped)
                continue

            if scope_stack:
                indent = scope_stack[-1][2]
            else:
                indent = 0
            fixed_lines.append(' ' * indent + stripped)

        return "\n".join(fixed_lines)
