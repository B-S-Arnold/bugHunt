import random
from .base import Bug

class ImportBug(Bug):
    def __init__(self, probability=1.0):
        self.probability = probability

    def inject(self, line: str) -> tuple[str, dict | None]:
        stripped = line.strip()
        if stripped.startswith("import") or stripped.startswith("from"):
            if random.random() < self.probability:
                modified_line = f"# {line}"
                return modified_line, {
                    "bug_type": "import",
                    "bug_action": "commented_out_import",
                    "original_line": line,
                    "modified_line": modified_line
                }
        return line, None
