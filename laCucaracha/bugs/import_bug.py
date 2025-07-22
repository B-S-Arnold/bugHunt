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

        if random.random() >= 1.0:  # or self.probability
            return line, None

        bug_subtype = random.choice(["comment", "remove", "swap_one", "swap_all"])
        modified_line = line
        original_line = line

        original_module = None
        replacement_module = None
        # comment mimics commenting out the import line
        if bug_subtype == "comment":
            modified_line = f"# {line}"
            
        # remove gets rid of the entire import line
        elif bug_subtype == "remove":
            modified_line = ""

        # swap_one replaces the import statement with a random alternative
        # swap_all mimics an incorrect import, replacing all instances
        elif bug_subtype in ("swap_one", "swap_all"):
            match = re.match(r"^\s*import\s+(\w+)", stripped)
            if match:
                original_module = match.group(1)
                all_modules = {
                    name for _, name, _ in pkgutil.iter_modules()
                }.union(set(sys.builtin_module_names))
                alternatives = list(all_modules - {original_module})

                if alternatives:
                    replacement_module = random.choice(alternatives)
                    modified_line = line.replace(original_module, replacement_module)
                else:
                    return line, None
            else:
                return line, None

        if modified_line != original_line:
            bug_info = {
                "bug_type": "import",
                "bug_subtype": bug_subtype,
                "original_line": original_line,
                "modified_line": modified_line
            }

            if bug_subtype in ("swap_one", "swap_all"):
                bug_info["original_module"] = original_module
                bug_info["replacement_module"] = replacement_module

                if bug_subtype == "swap_all":
                    bug_info["global_replace"] = {original_module: replacement_module}

            return modified_line, bug_info

        return line, None
