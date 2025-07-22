import random
import re
import pkgutil
import sys
from .base import Bug

class ImportBug(Bug):
    def inject(self, line: str) -> tuple[str, dict | None]:
        stripped = line.strip()
        if not (stripped.startswith("import") or stripped.startswith("from")):
            return line, None

        if random.random() >= 1.0:  # adjust probability if needed
            return line, None

        original_line = line
        modified_line = original_line
        bug_subtype = random.choice(["comment", "swap"])

        if bug_subtype == "comment":
            modified_line = f"# {original_line}"

        elif bug_subtype == "swap":
            match = re.match(r"^\s*import\s+(\w+)", stripped)
            if match:
                original_module = match.group(1)
                all_modules = {
                    name for _, name, _ in pkgutil.iter_modules()
                }.union(set(sys.builtin_module_names))
                alternatives = list(all_modules - {original_module})

                if alternatives:
                    replacement_module = random.choice(alternatives)
                    modified_line = original_line.replace(original_module, replacement_module)

        if modified_line != original_line:
            return modified_line, {
                "bug_type": "import",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }
        else:
            return line, None
