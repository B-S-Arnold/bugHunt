import re
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.block_stack = []
        self.expected_indent = 0

    def fix_line(self, line: str, line_number: int) -> str:
        original = line

        line = self._fix_spacing(line)
        line = self._fix_missing_colon(line, line_number)
        line = self._fix_indentation(line, line_number)

        if line != original:
            self.logs.append({
                "line_number": line_number,
                "original": original.rstrip(),
                "fixed": line.rstrip(),
                "fix_type": "formatting"
            })

        return line

    def _fix_spacing(self, line: str) -> str:
        line = re.sub(r'\s*([=+\-*/<>])\s*', r' \1 ', line)
        line = re.sub(r'\s*,\s*', ', ', line)
        line = re.sub(r'\s*:\s*', ': ', line)
        return line

    def _fix_missing_colon(self, line: str, line_number: int) -> str:
        stripped = line.strip()
        colon_keywords = ('def', 'if', 'for', 'while', 'try', 'except', 'with', 'elif', 'else', 'finally')
        if any(stripped.startswith(kw) for kw in colon_keywords) and not stripped.endswith(':'):
            line += ':'
            self.logs.append({
                "line_number": line_number,
                "original": stripped,
                "fixed": line.strip(),
                "fix_type": "missing_colon"
            })
        return line

    def _fix_indentation(self, line: str, line_number: int) -> str:
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip())

        block_keywords = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
        followup_keywords = ('except', 'else', 'elif', 'finally')
        block_body_starts = ('return', 'raise', 'pass', 'break', 'continue', 'yield')

        if any(stripped.startswith(kw) for kw in block_keywords):
            self.block_stack.append(current_indent)
            self.expected_indent = current_indent + 4
            return ' ' * current_indent + stripped

        if any(stripped.startswith(kw) for kw in followup_keywords):
            if self.block_stack:
                expected_indent = self.block_stack[-1]
                self.expected_indent = expected_indent + 4
                return ' ' * expected_indent + stripped

        if any(stripped.startswith(kw) for kw in block_body_starts):
            return ' ' * self.expected_indent + stripped

        if current_indent == 0 and self.block_stack:
            self.block_stack.clear()
            self.expected_indent = 0

        return ' ' * current_indent + stripped
