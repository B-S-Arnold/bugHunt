import random
import re
from .base import Bug

class FormatBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        original_line = line
        stripped = line.strip()

        if not stripped:
            return line, None  # skip empty lines

        if random.random() >= 1.0:  # or self.probability
            return line, None

        bug_subtype = random.choice(["indentation", "spacing", "extra_blank_line"])
        modified_line = line

        # indentation mimics incorrect indentation by adding or removing spaces at the start
        if bug_subtype == "indentation":
            if line.startswith(" "):
                modified_line = line.lstrip()
            else:
                modified_line = "    " + line

        # spacing mimics inconsistent spacing by adding or removing spaces
        elif bug_subtype == "spacing":
            spacing_targets = [
                r"\s*=\s*", r"\s*\+\s*", r"\s*-\s*", r"\s*\*\s*", r"\s*/\s*", 
                r"\s*==\s*", r"\s*,\s*", r"\s*:\s*"
            ]
            pattern = random.choice(spacing_targets)

            if re.search(pattern, line):
                if random.random() < 0.5:
                    modified_line = re.sub(pattern, pattern.strip(r"\s*"), line)
                else:
                    operator = re.sub(r"[\\\s*]", "", pattern)
                    modified_line = re.sub(pattern, f" {operator} ", line)

        # extra_blank_line mimics inserting an unnecessary blank line
        elif bug_subtype == "extra_blank_line":
            return line, {
                "bug_type": "format",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": original_line,
                "insert_blank_line_after": True  
            }

        if modified_line != original_line:
            return modified_line, {
                "bug_type": "format",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }

        return line, None
