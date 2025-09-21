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
        """General-purpose fallback formatter for any Python code"""
        lines = code.splitlines()
        if not lines:
            return code
        
        fixed_lines = []
        indent_stack = [0]  # Stack to track indentation levels
        
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
            
            # Determine the correct indentation level
            if first_word_clean in ('def', 'class'):
                # Functions and classes - determine nesting level
                indent_level = self._get_definition_level(fixed_lines)
                
            elif first_word_clean in ('except', 'finally'):
                # Align with matching try
                indent_level = self._find_try_block_indent(fixed_lines)
                
            elif first_word_clean in ('elif', 'else'):
                # Align with matching if
                indent_level = self._find_if_block_indent(fixed_lines)
                
            elif first_word_clean in block_starters:
                # Other block starters use current scope level
                indent_level = indent_stack[-1]
                
            else:
                # Regular statements
                indent_level = self._get_statement_level(fixed_lines, indent_stack)
            
            # Update the indent stack
            self._update_stack(indent_level, first_word_clean, block_starters, indent_stack)
            
            # Add missing colons
            if first_word_clean in block_starters and not stripped.endswith(':'):
                stripped += ':'
            
            # Apply indentation and add line
            spaces = indent_level * 4
            final_line = ' ' * spaces + stripped
            fixed_lines.append(final_line)
        
        return '\n'.join(fixed_lines)
    
    def _get_definition_level(self, previous_lines: list) -> int:
        """Determine the nesting level for a function or class definition"""
        if not previous_lines:
            return 0
        
        # Look backwards for the context
        for line in reversed(previous_lines):
            if line.strip():
                current_indent = (len(line) - len(line.lstrip())) // 4
                first_word = line.strip().split()[0].rstrip(':')
                
                # If we're inside a class or function, nest one level deeper
                if first_word in ('class', 'def'):
                    return current_indent + 1
                # If we find a non-block statement at level 0, this def should be at level 0
                elif current_indent == 0 and first_word not in ('if', 'for', 'while', 'try', 'with'):
                    return 0
                # If we're inside any other block, stay at that level
                elif first_word in ('if', 'for', 'while', 'try', 'with', 'except', 'finally'):
                    return current_indent
                    
        return 0
    
    def _get_statement_level(self, previous_lines: list, indent_stack: list) -> int:
        """Determine indentation level for a regular statement"""
        if not previous_lines:
            return 0
        
        # Find the most recent block context
        for line in reversed(previous_lines):
            if line.strip():
                line_indent = (len(line) - len(line.lstrip())) // 4
                first_word = line.strip().split()[0].rstrip(':')
                
                # If previous line was a block starter, we go inside it
                if first_word in ('def', 'class', 'if', 'for', 'while', 'try', 'with', 'except', 'finally', 'elif', 'else'):
                    return line_indent + 1
                
                # If previous line was a regular statement, same level
                else:
                    return line_indent
        
        return 0
    
    def _update_stack(self, current_level: int, first_word_clean: str, block_starters: set, indent_stack: list):
        """Update the indentation stack based on current context"""
        # Pop levels that are deeper than current level
        while len(indent_stack) > 1 and indent_stack[-1] > current_level:
            indent_stack.pop()
        
        # Ensure we have the current level
        if not indent_stack or indent_stack[-1] != current_level:
            if indent_stack:
                indent_stack[-1] = current_level
            else:
                indent_stack.append(current_level)
        
        # If this line starts a new block, add the next level
        if first_word_clean in block_starters:
            indent_stack.append(current_level + 1)

    def _find_try_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching try statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0].rstrip(':')  # Remove colon
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
                first_word = stripped.split()[0].rstrip(':')  # Remove colon
                if first_word in ('if', 'elif'):
                    spaces = len(line) - len(line.lstrip())
                    return spaces // 4
        return 0