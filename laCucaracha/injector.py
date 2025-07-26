import random
import os
import re
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
            FormatBug()
        ]
        self.logs = []  

    def inject_bugs(self, code: str, source_path: Optional[str] = None) -> str:
        lines = code.split("\n")
        total_bugs = max(1, len(lines) // self.config.bugs_per_lines)

        valid_lines = [i for i, line in enumerate(lines) if line.strip()]
        if not valid_lines:
            return code

        chosen_lines = random.sample(valid_lines, min(total_bugs, len(valid_lines)))

        empty_line_indices = set()
        
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
        
                if modified_line.strip() == "":
                    empty_line_indices.add(line_no)
                
                if "global_replace" in diff:
                    for old, new in diff["global_replace"].items():
                        for i, l in enumerate(lines):
                            if i == line_no:
                                continue  
                            lines[i] = re.sub(rf"\b{re.escape(old)}\b", new, lines[i])
                            
                if diff.get("insert_blank_line_after"):
                    lines.insert(line_no + 1, "")


        lines = [line for idx, line in enumerate(lines) if idx not in empty_line_indices]

        modified_code = "\n".join(lines)

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

            for log in sorted(self.logs, key=lambda l: l.get("line_number", float("inf"))):
                line_no = log.get("line_number", "unknown")
                bug_type = log.get("bug_type", "unknown")
                bug_subtype = log.get("bug_subtype", "")

                original = log.get("original_word") or log.get("original_line") or "N/A"
                modified = log.get("modified_word") or log.get("modified_line") or "N/A"

                f.write(f"- Line {line_no}: \"{original}\" → \"{modified}\" (type: {bug_type}, subtype: {bug_subtype})\n")

            f.write("\n--- Original Code ---\n")
            f.write(original_code)
            f.write("\n\n--- Modified Code ---\n")
            f.write(modified_code)
