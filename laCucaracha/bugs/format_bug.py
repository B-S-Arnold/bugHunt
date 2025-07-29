import random
import re
from .base import Bug

class FormatBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        original_line = line
        stripped = line.strip()

        if not stripped:
            return line, None  # skip empty lines

        if random.random() >= 1.0:
            return line, None

        bug_subtype = random.choice(["indent_soft", "spacing", "extra_blank_line", "block_indent"])
        modified_line = line

        # indent_soft: mimics inconsistent indentation style on single line
        if bug_subtype == "indent_soft":
            if line.startswith("    "):
                modified_line = "  " + line[4:]
            elif line.startswith("\t"):
                modified_line = line.replace("\t", "    ", 1)
            else:
                modified_line = line

        # spacing: mimics inconsistent spacing by adding or removing spaces
        elif bug_subtype == "spacing":
            spacing_map = {
                r"\s*=\s*": "=",
                r"\s*\+\s*": "+",
                r"\s*-\s*": "-",
                r"\s*\*\s*": "*",
                r"\s*/\s*": "/",
                r"\s*==\s*": "==",
                r"\s*,\s*": ",",
                r"\s*:\s*": ":"
            }

            pattern, operator = random.choice(list(spacing_map.items()))

            if re.search(pattern, line):
                if random.random() < 0.5:
                    modified_line = re.sub(pattern, operator, line)
                else:
                    modified_line = re.sub(pattern, f" {operator} ", line)

        # extra_blank_line: mimics inserting an unnecessary blank line
        elif bug_subtype == "extra_blank_line":
            return line, {
                "bug_type": "format",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": original_line,
                "insert_blank_line_after": True  
            }

        # block_indent: mimic increasing indentation for a full block (handled in injector)
        elif bug_subtype == "block_indent":
            # Only indent if it's a valid block start
            block_starters = ("def ", "if ", "elif ", "else", "try", "with", "for ", "while ")
            safe = any(stripped.startswith(start) for start in block_starters)

            if not safe:
                return line, None  # skip invalid block-indents

            modified_line = "    " + line  # Pre-indent starting line

            return modified_line, {
                "bug_type": "format",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }


        if modified_line != original_line:
            return modified_line, {
                "bug_type": "format",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }

        return line, None
