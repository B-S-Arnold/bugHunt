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
        scope_stack = []  # (scope_type, opener_indent, body_indent)

        lines = code.splitlines()

        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                fixed_lines.append("")
                continue

            leading_spaces = len(line) - len(stripped)
            block_openers = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
            block_followups = ('elif', 'else', 'except', 'finally')

            first_word = stripped.split()[0]

            # Pop scopes if current line is before opener_indent
            while scope_stack and leading_spaces < scope_stack[-1][1]:
                scope_stack.pop()

            # Handle followups (except/else/elif/finally)
            if first_word in block_followups:
                # Find nearest matching opener (try/if/for/etc.)
                for i in range(len(scope_stack)-1, -1, -1):
                    if scope_stack[i][0] in ('if', 'for', 'while', 'try', 'with'):
                        opener_indent = scope_stack[i][1]
                        break
                else:
                    opener_indent = 0

                if not stripped.endswith(':'):
                    stripped += ':'

                scope_stack.append((first_word, opener_indent, opener_indent + 4))
                fixed_lines.append(' ' * opener_indent + stripped)
                continue

            # Handle block openers (def/class/if/etc.)
            if first_word in block_openers:
                if not stripped.endswith(':'):
                    stripped += ':'

                # Determine opener indent
                if first_word in ('def', 'class'):
                    # top-level def/class always 0 indent
                    opener_indent = 0
                else:
                    # other blocks align with nearest parent or use current leading_spaces
                    parent_body_indent = scope_stack[-1][2] if scope_stack else 0
                    opener_indent = max(leading_spaces, parent_body_indent)

                body_indent = opener_indent + 4
                scope_stack.append((first_word, opener_indent, body_indent))
                fixed_lines.append(' ' * opener_indent + stripped)
                continue

            # Normal line
            if scope_stack:
                indent = max(leading_spaces, scope_stack[-1][2])
            else:
                indent = leading_spaces
            fixed_lines.append(' ' * indent + stripped)

        return "\n".join(fixed_lines)
