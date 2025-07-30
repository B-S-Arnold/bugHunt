import random
import re
from .base import Bug

class LogicBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        original_line = line
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            return line, None

        if random.random() >= 1.0:
            return line, None

        bug_subtype = random.choice(["bool_flip", "comparison_swap", "off_by_one"])
        modified_line = line

        # Flip boolean literals True <-> False
        if bug_subtype == "bool_flip":
            if "True" in line:
                modified_line = line.replace("True", "False", 1)
            elif "False" in line:
                modified_line = line.replace("False", "True", 1)

        # Swap comparison operators (== -> !=, < -> >)
        elif bug_subtype == "comparison_swap":
            swap_map = {
                "==": "!=",
                "!=": "==",
                "<=": ">=",
                ">=": "<=",
                "<": ">",
                ">": "<"
            }

            for op, swapped in swap_map.items():
                pattern = r"(?<![<>=!])\s*" + re.escape(op) + r"\s*(?![<>=!])"
                if re.search(pattern, line):
                    modified_line = re.sub(pattern, f" {swapped} ", line, count=1)
                    break

        # Off-by-one errors: +1/-1 around indexing or range()
        elif bug_subtype == "off_by_one":
            range_match = re.search(r"range\(\s*([^)]+?)\s*\)", line)
            if range_match:
                inner = range_match.group(1).strip()
                if inner.count('(') <= 1 and inner.count(')') <= 1:
                    if re.search(r"[\+\-]\s*1", inner):
                        if "+1" in inner.replace(" ", ""):
                            new_inner = re.sub(r"\+\s*1", "-1", inner)
                        else:
                            new_inner = re.sub(r"\-\s*1", "+1", inner)
                    else:
                        op = random.choice([" + 1", " - 1"])
                        new_inner = inner + op

                    modified_line = line.replace(f"range({inner})", f"range({new_inner})")

        if modified_line != original_line:
            return modified_line, {
                "bug_type": "logic",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }

        return line, None
