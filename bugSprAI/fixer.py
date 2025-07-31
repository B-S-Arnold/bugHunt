import re

class RuleBasedFixer:
    def __init__(self):
        self.rules = [
            self.fix_assignment_in_condition,
            self.fix_off_by_one_range,
            self.fix_boolean_literals,
            self.fix_comparison_swap,
            self.fix_indentation,
        ]

    def fix_code(self, code: str) -> str:
        lines = code.split("\n")
        fixed_lines = []

        for line in lines:
            original = line
            for rule in self.rules:
                line = rule(line)
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_assignment_in_condition(self, line: str) -> str:
        if re.search(r"\bif\s+.*[^=!<>]=[^=].*:", line):
            return line.replace("=", "==", 1)
        return line

    def fix_off_by_one_range(self, line: str) -> str:
        match = re.search(r"range\(([^)]+)\)", line)
        if match:
            inner = match.group(1)
            if inner.isdigit():
                return line.replace(f"range({inner})", f"range({inner} - 1)")
        return line

    def fix_boolean_literals(self, line: str) -> str:
        if " if True:" in line or " if False:" in line:
            return line.replace("True", "condition").replace("False", "not condition")
        return line

    def fix_comparison_swap(self, line: str) -> str:
        swaps = {
            "!=": "==",
            "==": "!=",
            "<": ">",
            ">": "<"
        }
        for k, v in swaps.items():
            pattern = r"\b" + re.escape(k) + r"\b"
            if re.search(pattern, line):
                return re.sub(pattern, v, line, count=1)
        return line

    def fix_indentation(self, line: str) -> str:
        if line.lstrip().startswith(("except", "return", "print")) and line.startswith("    ") == False:
            return "    " + line
        return line
