import re
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.block_stack = []

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

        block_keywords = ('def', 'class', 'if', 'for', 'while', 'try', 'with')
        followup_keywords = ('except', 'else', 'elif', 'finally')

        current_indent = len(line) - len(line.lstrip())

        # Handle block openers (like def, try)
        if any(stripped.startswith(kw) for kw in block_keywords):
            self.block_stack.append(current_indent)
            return line

        # Handle block closers (like except)
        if any(stripped.startswith(kw) for kw in followup_keywords):
            if self.block_stack:
                expected_indent = self.block_stack[-1]
                corrected_line = ' ' * expected_indent + stripped
                if corrected_line != line:
                    self.logs.append({
                        "line_number": line_number,
                        "original": line.rstrip(),
                        "fixed": corrected_line.rstrip(),
                        "fix_type": "indentation_fix"
                    })
                    return corrected_line

        # Clear stack on dedent
        if current_indent == 0 and self.block_stack:
            self.block_stack.clear()

        return line
