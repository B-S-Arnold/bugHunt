import ast
from .base_fixer import BaseFixer

class FormatFixer(BaseFixer):
    def __init__(self):
        super().__init__()
        self.used_ast = False

    def fix_code(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            self.used_ast = True
            formatted = ast.unparse(tree)
            return self._final_format_pass(formatted)
        except SyntaxError:
            self.used_ast = False
            return self.fallback_format(code)

    def _final_format_pass(self, code: str) -> str:
        """Clean up any minor formatting issues from ast.unparse"""
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
        """Fallback formatter with proper try/except handling (no debug prints)"""
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
            first_word_clean = first_word.rstrip(':')
            
            if first_word_clean in ('except', 'finally'):
                try_indent_level = self._find_try_block_indent(fixed_lines)
                current_indent = try_indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = try_indent_level + 1
                
            elif first_word_clean in ('elif', 'else'):
                if_indent_level = self._find_if_block_indent(fixed_lines)
                current_indent = if_indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = if_indent_level + 1
                
            elif first_word_clean in ('def', 'class'):
                indent_level = 0
                current_indent = 0
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = 1
                
            elif first_word_clean in block_starters:
                current_indent = indent_level * 4
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level += 1
                
            else:
                current_indent = indent_level * 4
            
            final_line = ' ' * current_indent + stripped
            fixed_lines.append(final_line)
        
        return '\n'.join(fixed_lines)

    def _find_try_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching try statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0].rstrip(':')
                if first_word == 'try':
                    spaces = len(line) - len(line.lstrip())
                    level = spaces // 4
                    return level
        return 0

    def _find_if_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching if statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0].rstrip(':')
                if first_word in ('if', 'elif'):
                    spaces = len(line) - len(line.lstrip())
                    return spaces // 4
        return 0