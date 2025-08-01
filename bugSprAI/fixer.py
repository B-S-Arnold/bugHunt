import re

class BugFixer:

    def fix_line(self, line: str) -> str:
        """
        Very basic rule-based fixer. Expands later.
        """
        # Fix common logic bugs
        line = self._fix_logic_bugs(line)

        # Fix basic formatting issues
        line = self._fix_formatting(line)

        # Fix common typos
        line = self._fix_typos(line)

        return line

    def _fix_logic_bugs(self, line: str) -> str:
        # Reverse logic errors
        line = re.sub(r'!=', '==', line)
        line = re.sub(r'>=', '<=', line)
        line = re.sub(r'<=', '>=', line)
        line = re.sub(r'True', 'False', line)
        line = re.sub(r'False', 'True', line)
        line = re.sub(r'range\(([^)]+)\s*\+\s*1\)', r'range(\1)', line)
        return line

    def _fix_formatting(self, line: str) -> str:
        # Normalize spacing around operators
        line = re.sub(r'\s*([=+\-*/<>])\s*', r' \1 ', line)
        line = re.sub(r'\s*,\s*', ', ', line)
        line = re.sub(r'\s*:\s*', ': ', line)
        return line

    def _fix_typos(self, line: str) -> str:
        typo_map = {
            "pritn": "print",
            "retrun": "return",
            "improt": "import",
            "defn": "def"
        }
        for typo, correct in typo_map.items():
            line = re.sub(rf'\b{typo}\b', correct, line)
        return line

    def fix_code(self, code: str) -> str:
        lines = code.splitlines()
        fixed_lines = [self.fix_line(line) for line in lines]
        return "\n".join(fixed_lines)
