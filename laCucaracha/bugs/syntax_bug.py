import random
import re
from .base import Bug

class SyntaxBug:
    def inject(self, line: str):
        
        return line, None