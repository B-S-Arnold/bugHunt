import random
import os
from typing import Optional
from bugs.typo_bug import TypoBug
# from bugs.import_bug import ImportBug
from config import BugInjectionConfig

class BugInjector:
    def __init__(self, config: BugInjectionConfig):
        self.config = config
        if config.seed is not None:
            random.seed(config.seed)
        self.bug_classes = [TypoBug()] # add more bug subclasses
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
            for log in self.logs:
                f.write(f"- Line {log['line_number']}: \"{log['original_word']}\" → \"{log['modified_word']}\" "
                        f"(type: {log['typo_type']})\n")

            f.write("\n--- Original Code ---\n")
            f.write(original_code)
            f.write("\n\n--- Modified Code ---\n")
            f.write(modified_code)