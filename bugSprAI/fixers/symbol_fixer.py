import re
from .base_fixer import BaseFixer

class SymbolFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
        original = line
        pairs = {'(': ')', '[': ']', '{': '}'}
        open_stack = []

        for i, char in enumerate(line):
            if char in pairs:
                open_stack.append((char, i))
            elif char in pairs.values():
                if open_stack and pairs[open_stack[-1][0]] == char:
                    open_stack.pop()

        fixed = line
        for open_char, index in reversed(open_stack):
            close_char = pairs[open_char]

            if re.match(r'^\s*(def|if|for|while|with)\b', line) and not line.strip().endswith(':'):
                if not fixed.strip().endswith(close_char + ':'):
                    fixed = fixed.rstrip(':')
                    fixed += close_char + ':'
            else:
                fixed += close_char

        if fixed != original:
            self.logs.append({
                "line_number": line_number,
                "original": original.strip(),
                "fixed": fixed.strip(),
                "fix_type": "symbol_balance"
            })

        return fixed
