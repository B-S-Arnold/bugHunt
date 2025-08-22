import keyword
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self, indent_size=4):
        super().__init__()
        self.indent_stack = []
        self.scope_stack = []
        self.indent_size = indent_size

        self.block_openers = {"def", "class", "if", "for", "while", "try", "with"}
        self.block_followups = {"elif", "else", "except", "finally"}
        self.block_terminators = {"return", "pass", "break", "continue", "raise"}

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
            return ""

        first_word = stripped.split()[0]

        if first_word in self.block_followups:
            if self.indent_stack:
                indent = self.indent_stack[-1] - self.indent_size
            else:
                indent = 0
            if not stripped.endswith(":"):
                stripped += ":"
            return " " * indent + stripped

        if first_word in self.block_openers:
            if not stripped.endswith(":"):
                stripped += ":"
            indent = self.indent_stack[-1] if self.indent_stack else 0
            self.indent_stack.append(indent + self.indent_size)
            return " " * indent + stripped

        if first_word in self.block_terminators:
            indent = self.indent_stack[-1] - self.indent_size if self.indent_stack else 0
            if self.indent_stack:
                self.indent_stack.pop()
            return " " * indent + stripped

        indent = self.indent_stack[-1] if self.indent_stack else 0
        return " " * indent + stripped
