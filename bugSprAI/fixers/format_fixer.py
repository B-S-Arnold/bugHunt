import re
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def fix_line(self, line: str, line_number: int) -> str:
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
