import ast
from .base_fixer import BaseFixer

class IndentFixer(BaseFixer):
    def fix_code(self, code: str) -> str:
        lines = code.splitlines()
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fixed_lines.append('')
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            normalized_indent = (current_indent // 4) * 4
            if current_indent % 4 != 0 and current_indent > 0:
                normalized_indent = ((current_indent // 4) + 1) * 4
            
            fixed_lines.append(' ' * normalized_indent + stripped)
        
        return '\n'.join(fixed_lines)