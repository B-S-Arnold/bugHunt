import re
from .base_fixer import BaseFixer

class LogicFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
        original = line
        fixes = [
            (r'!=', '=='),
            (r'>=', '<='),
            (r'<=', '>='),
            (r'\bTrue\b', 'False'),
            (r'\bFalse\b', 'True'),
            (r'range\(([^)]+)\s*\+\s*1\)', r'range(\1)')
        ]
        for pattern, replacement in fixes:
            if re.search(pattern, line):
                fixed_line = re.sub(pattern, replacement, line)
                self.logs.append({
                    "line_number": line_number,
                    "original": line.strip(),
                    "fixed": fixed_line.strip(),
                    "fix_type": "logic_bug_fix"
                })
                line = fixed_line
        return line
