import random
import re
from .base import Bug

class SyntaxBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return line, None

        if random.random() >= 1.0:
            return line, None

        bug_subtype = random.choice([
            "missing_colon",
            "unclosed_paren",
            "extra_comma"
        ])
        modified_line = line

        # missing_colon removes colon from lines that require it
        if bug_subtype == "missing_colon":
            if re.match(r"^(if|elif|else|for|while|def|class)\b.*:\s*$", stripped):
                modified_line = re.sub(r":\s*$", "", line)

        # unclosed_paren removes a closing parenthesis
        elif bug_subtype == "unclosed_paren":
            if "(" in line and ")" in line:
                modified_line = line[::-1].replace(")", "", 1)[::-1]

        # extra_comma adds an unnecessary comma in argument or list/tuple
        elif bug_subtype == "extra_comma":
            match = re.search(r"\((.*?)\)", line)
            if match:
                contents = match.group(1)
                parts = contents.split(",")
                if len(parts) > 1:
                    insert_at = random.randint(0, len(parts) - 2)
                    parts.insert(insert_at + 1, "")
                    modified = ",".join(parts)
                    modified_line = line.replace(contents, modified)

        if modified_line != line:
            return modified_line, {
                "bug_type": "syntax",
                "bug_subtype": bug_subtype,
                "original_line": line,
                "modified_line": modified_line
            }

        return line, None
