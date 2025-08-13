import re
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.indent_stack = []  # Tracks base indent for current scope
        self.scope_type_stack = []  # Tracks what kind of scope we're in

    def fix_code(self, code: str) -> str:
        """Fixes indentation in a multi-line aware pass."""
        fixed_lines = []
        self.indent_stack = []
        self.scope_type_stack = []

        lines = code.splitlines()

        for i, line in enumerate(lines):
            fixed_lines.append(self.fix_line(line, i + 1))

        return "\n".join(fixed_lines)

    def fix_line(self, line: str, line_number: int) -> str:
        original = line
        stripped = line.strip()

        if not stripped:
            return stripped

        # Common block openers
        block_openers = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
        block_followups = ('except', 'else', 'elif', 'finally')
        block_body_starts = ('return', 'raise', 'pass', 'break', 'continue', 'yield')

        # Check if closing a scope (dedent)
        while self.scope_type_stack and not stripped.startswith(self.scope_type_stack[-1]):
            self.indent_stack.pop()
            self.scope_type_stack.pop()

        # Adjust indent based on scope
        indent_level = self.indent_stack[-1] if self.indent_stack else 0

        # Detect function/class definition
        if any(stripped.startswith(kw) for kw in ('def', 'class')):
            if not stripped.endswith(':'):
                stripped += ':'
            indent_level = 0
            self.indent_stack.append(indent_level)
            self.scope_type_stack.append(('def' if stripped.startswith('def') else 'class'))
            return ' ' * indent_level + stripped

        # Detect block openers (inside any scope)
        if any(stripped.startswith(kw) for kw in block_openers):
            if not stripped.endswith(':'):
                stripped += ':'
            # If inside a function, increase indent by one extra tab
            if self.scope_type_stack and self.scope_type_stack[-1] == 'def':
                indent_level = self.indent_stack[-1] + 4
            self.indent_stack.append(indent_level)
            self.scope_type_stack.append(stripped.split()[0])
            return ' ' * indent_level + stripped

        # Detect follow-up blocks
        if any(stripped.startswith(kw) for kw in block_followups):
            if not stripped.endswith(':'):
                stripped += ':'
            # Match parent indent (e.g., except aligns with try)
            if self.indent_stack:
                indent_level = self.indent_stack[-1]
            # If we're inside a function, shift it over one tab
            if self.scope_type_stack and 'def' in self.scope_type_stack:
                indent_level += 4
            return ' ' * indent_level + stripped

        # Detect block body statements
        if any(stripped.startswith(kw) for kw in block_body_starts):
            if self.scope_type_stack:
                # One tab deeper than current scope
                indent_level = self.indent_stack[-1] + 4
                if 'def' in self.scope_type_stack:
                    indent_level += 4
            else:
                indent_level = 4
            return ' ' * indent_level + stripped

        # Default case: regular statement inside scope
        if self.scope_type_stack:
            indent_level = self.indent_stack[-1] + 4
            if 'def' in self.scope_type_stack:
                indent_level += 4

        return ' ' * indent_level + stripped
