import random
from bugs.typo_bug import TypoBug
# from bugs.import_bug import ImportBug
from config import BugInjectionConfig

class BugInjector:
    def __init__(self, config: BugInjectionConfig):
        self.config = config
        if config.seed is not None:
            random.seed(config.seed)
        self.bug_classes = [TypoBug()]  # more bug subclasses

    def inject_bugs(self, code: str) -> str:
        lines = code.split("\n")
        total_bugs = max(1, len(lines) // self.config.bugs_per_lines)

        valid_lines = [i for i, line in enumerate(lines) if line.strip()]
        if not valid_lines:
            return code

        chosen_lines = random.sample(valid_lines, min(total_bugs, len(valid_lines)))

        for line_no in chosen_lines:
            bug = random.choice(self.bug_classes)
            lines[line_no] = bug.inject(lines[line_no])

        return "\n".join(lines)