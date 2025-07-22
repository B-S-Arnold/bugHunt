import random
import os
from typing import Optional
from bugs import *
from config import BugInjectionConfig

class BugInjector:
    def __init__(self, config: BugInjectionConfig):
        self.config = config
        if config.seed is not None:
            random.seed(config.seed)
        self.bug_classes = [
            TypoBug(),
            ImportBug(),
            ]
        self.logs = []  # list of all injected bug info

    def inject_bugs(self, code: str, source_path: Optional[str] = None) -> str:
        lines = code.split("\n")
        total_bugs = max(1, len(lines) // self.config.bugs_per_lines)

        valid_lines = [i for i, line in enumerate(lines) if line.strip()]
        if not valid_lines:
            return code

        chosen_lines = random.sample(valid_lines, min(total_bugs, len(valid_lines)))

        for line_no in chosen_lines:
            bug = random.choice(self.bug_classes)
            original_line = lines[line_no]
            modified_line, diff = bug.inject(original_line)

            if diff:
                lines[line_no] = modified_line
                self.logs.append({
                    "line_number": line_no + 1,
                    "original_line": original_line,
                    "modified_line": modified_line,
                    **diff
                })

        modified_code = "\n".join(lines)

        # Optionally save log
        if source_path:
            self._save_log(source_path, code, modified_code)

        return modified_code

    def _save_log(self, source_path: str, original_code: str, modified_code: str):
        base_name = os.path.basename(source_path)
        dir_name = os.path.dirname(source_path)
        log_path = os.path.join(dir_name, f"{base_name}_bug_log.txt")

        with open(log_path, "w") as f:
            f.write(f"Original File: {base_name}\n")
            f.write(f"Bug Log ({len(self.logs)} bugs):\n\n")

            # 🔽 Sort logs by line number before writing
            for log in sorted(self.logs, key=lambda l: l.get("line_number", float("inf"))):
                line_no = log.get("line_number", "unknown")
                bug_type = log.get("bug_type", "unknown")

                original = log.get("original_word") or log.get("original_line") or "N/A"
                modified = log.get("modified_word") or log.get("modified_line") or "N/A"

                extra_info = ""
                if bug_type == "typo" and "typo_type" in log:
                    extra_info = f"(typo_type: {log['typo_type']})"

                f.write(f"- Line {line_no}: \"{original}\" → \"{modified}\" (type: {bug_type}) {extra_info}\n")

            f.write("\n--- Original Code ---\n")
            f.write(original_code)
            f.write("\n\n--- Modified Code ---\n")
            f.write(modified_code)
