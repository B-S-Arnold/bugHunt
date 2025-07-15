from enum import Enum
from dataclasses import dataclass

class BugSeverity(Enum):
    TRIVIAL = 1
    MODERATE = 2
    CRITICAL = 3

@dataclass
class BugInjectionConfig:
    bugs_per_lines: int
    severity: BugSeverity
    seed: int = None