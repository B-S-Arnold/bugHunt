import ast
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.used_ast = False  # track if AST succeeded

    def fix_code(self, code: str) -> str:
        # --- First try AST reformatting ---
        try:
            tree = ast.parse(code)
            self.used_ast = True
            return ast.unparse(tree)
        except SyntaxError:
            self.used_ast = False
            return self.fallback_format(code)

    def fallback_format(self, code: str) -> str:
        """Indentation fixer (only used if AST parse fails)."""
        fixed_lines = []
        indent_stack = []
        scope_stack = []

        lines = code.splitlines()

        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                fixed_lines.append("")
                continue

            leading_spaces = len(line) - len(stripped)

            while indent_stack and leading_spaces < indent_stack[-1]:
                indent_stack.pop()
                scope_stack.pop()

            block_openers = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
            block_followups = ('elif', 'else', 'except', 'finally')

            first_word = stripped.split()[0]

            if first_word in block_followups:
                if indent_stack:
                    indent_stack.pop()
                    indent = indent_stack[-1] if indent_stack else 0
                else:
                    indent = 0
                if not stripped.endswith(':'):
                    stripped += ':'
                indent_stack.append(indent + 4)
                scope_stack.append(first_word)
                fixed_lines.append(' ' * indent + stripped)
                continue


            if first_word in block_openers:
                if indent_stack:
                    indent_stack.pop()
                    indent = indent_stack[-1] if indent_stack else 0
                else:
                    indent = 0
                if not stripped.endswith(':'):
                    stripped += ':'
                indent = leading_spaces
                indent_stack.append(indent + 4)
                scope_stack.append(first_word)
                fixed_lines.append(' ' * indent + stripped)
                continue

            indent = indent_stack[-1] if indent_stack else 0
            fixed_lines.append(' ' * indent + stripped)

        return "\n".join(fixed_lines)
