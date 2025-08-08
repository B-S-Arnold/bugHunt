import re
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
        original = line
        fixed = self._fix_formatting(line, line_number)
        fixed = self._fix_indentation(fixed, line_number)
        return fixed

    def _fix_formatting(self, line: str, line_number: int) -> str:
        original = line
        fixed = re.sub(r'\s*([=+\-*/<>])\s*', r' \1 ', line)
        fixed = re.sub(r'\s*,\s*', ', ', fixed)
        fixed = re.sub(r'\s*:\s*', ': ', fixed)
        if fixed != original:
            self.logs.append({
                "line_number": line_number,
                "original": original.strip(),
                "fixed": fixed.strip(),
                "fix_type": "formatting"
            })
        return fixed

    def _fix_indentation(self, line: str, line_number: int) -> str:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        block_keywords = ['def', 'if', 'for', 'while', 'try', 'except', 'with', 'class', 'elif', 'else']

        if any(stripped.startswith(kw) for kw in block_keywords):
            if indent > 0:
                fixed_line = stripped
                if not fixed_line.strip().endswith(':'):
                    fixed_line = fixed_line.rstrip() + ':'
                self.logs.append({
                    "line_number": line_number,
                    "original": line.strip(),
                    "fixed": fixed_line.strip(),
                    "fix_type": "indentation_block_start"
                })
                return fixed_line

        if any(
            re.match(r'^\s*(return|raise|pass|break|continue|print|yield)\b', stripped)
        ):
            if indent == 0:
                fixed_line = '    ' + stripped
                self.logs.append({
                    "line_number": line_number,
                    "original": line.strip(),
                    "fixed": fixed_line.strip(),
                    "fix_type": "indentation_block_body"
                })
                return fixed_line

        return line
