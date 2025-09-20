import ast
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.used_ast = False

    def fix_code(self, code: str) -> str:
        try:
            # First, try AST parsing and unparsing
            tree = ast.parse(code)
            self.used_ast = True
            formatted = ast.unparse(tree)
            
            return self._final_format_pass(formatted)
        except SyntaxError:
            self.used_ast = False
            return self.fallback_format(code)

    def _final_format_pass(self, code: str) -> str:
        lines = code.splitlines()
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip())
                cleaned_content = ' '.join(line.strip().split())
                fixed_lines.append(' ' * leading_spaces + cleaned_content)
            else:
                fixed_lines.append('')
        
        return '\n'.join(fixed_lines)

    def fallback_format(self, code: str) -> str:
        lines = code.splitlines()
        if not lines:
            return code
            
        fixed_lines = []
        indent_level = 0
        
        block_starters = {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 
            'try', 'except', 'finally', 'with', 'match', 'case'
        }
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not stripped:
                fixed_lines.append('')
                continue
            
            first_word = stripped.split()[0] if stripped else ''
            
            if first_word in ('except', 'finally'):
                try_indent_level = self._find_try_block_indent(fixed_lines)
                current_indent = try_indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = try_indent_level + 1
                
            elif first_word in ('elif', 'else'):
                if_indent_level = self._find_if_block_indent(fixed_lines)
                current_indent = if_indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = if_indent_level + 1
                
            elif first_word in ('def', 'class'):
                indent_level = 0
                current_indent = 0
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = 1
                
            elif first_word in block_starters:
                current_indent = indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level += 1
                
            else:
                current_indent = indent_level * 4
            
            fixed_lines.append(' ' * current_indent + stripped)
        
        return '\n'.join(fixed_lines)
    
    def _find_if_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level of the matching if statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0]
                if first_word in ('if', 'elif'):
                    return (len(line) - len(line.lstrip())) // 4
        return 0
    
    def _find_try_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching try statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0]
                if first_word == 'try':
                    spaces = len(line) - len(line.lstrip())
                    return spaces // 4  # Convert spaces to indent level
        return 0