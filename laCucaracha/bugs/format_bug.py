import random
import re
from .base import Bug

class FormatBug:
    def inject(self, line: str):
        
        return line, None