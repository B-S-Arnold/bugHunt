from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.indent_stack = []  
        self.scope_stack = []   

    def fix_code(self, code: str) -> str:
        fixed_lines = []
        self.indent_stack = []
        self.scope_stack = []

        lines = code.splitlines()

        for line in lines:
            fixed_lines.append(self.fix_line(line))

        return "\n".join(fixed_lines)

    def fix_line(self, line: str) -> str:
        stripped = line.lstrip()
        if not stripped:
            # blank line, keep blank
            return ""

        leading_spaces = len(line) - len(stripped)

        while self.indent_stack and leading_spaces < self.indent_stack[-1]:
            self.indent_stack.pop()
            self.scope_stack.pop()

        block_openers = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
        block_followups = ('elif', 'else', 'except', 'finally')
        needs_colon = False

        first_word = stripped.split()[0]

        if first_word in block_followups:
            if self.indent_stack:
                if self.scope_stack:
                    self.scope_stack.pop()
                if self.indent_stack:
                    self.indent_stack.pop()
            expected_indent = self.indent_stack[-1] if self.indent_stack else 0
            indent = expected_indent
            if not stripped.endswith(':'):
                stripped += ':'
            self.indent_stack.append(indent)
            self.scope_stack.append(first_word)
            return ' ' * indent + stripped

        if first_word in block_openers:
            if not stripped.endswith(':'):
                stripped += ':'
            indent = leading_spaces
            self.indent_stack.append(indent + 4)
            self.scope_stack.append(first_word)
            return ' ' * indent + stripped

        if first_word in ('def', 'class') and not self.indent_stack:
            if not stripped.endswith(':'):
                stripped += ':'
            self.indent_stack.append(4)
            self.scope_stack.append(first_word)
            return ' ' * 0 + stripped

        indent = self.indent_stack[-1] if self.indent_stack else 0

        return ' ' * indent + stripped
