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
        """Fallback formatter with proper scope tracking"""
        lines = code.splitlines()
        if not lines:
            return code
            
        fixed_lines = []
        indent_stack = [0]  # Stack of indentation levels
        
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
            
            # Calculate what the current indentation should be based on content
            expected_indent = self._calculate_expected_indent(
                first_word_clean, fixed_lines, indent_stack
            )
            
            # Update the indent stack based on the expected indentation
            self._update_indent_stack(expected_indent, indent_stack)
            
            # Add colon if missing for block starters
            if first_word_clean in block_starters and not stripped.endswith(':'):
                stripped += ':'
            
            # Apply indentation
            current_indent = expected_indent * 4
            final_line = ' ' * current_indent + stripped
            fixed_lines.append(final_line)
            
            # If this line starts a new block, prepare for indented content
            if first_word_clean in block_starters:
                indent_stack.append(expected_indent + 1)
        
        return '\n'.join(fixed_lines)

    def _calculate_expected_indent(self, first_word_clean: str, previous_lines: list, indent_stack: list) -> int:
        """Calculate the expected indentation level for a line"""
        
        # Special cases that align with their matching blocks
        if first_word_clean in ('except', 'finally'):
            return self._find_try_block_indent(previous_lines)
        elif first_word_clean in ('elif', 'else'):
            return self._find_if_block_indent(previous_lines)
        elif first_word_clean in ('def', 'class'):
            return 0  # Top-level
        elif first_word_clean in {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 
                                  'try', 'except', 'finally', 'with', 'match', 'case'}:
            # Other block starters use current level
            return indent_stack[-1] if indent_stack else 0
        else:
            # Regular statements use current level
            return indent_stack[-1] if indent_stack else 0

    def _update_indent_stack(self, expected_indent: int, indent_stack: list):
        """Update the indent stack to match the expected indentation level"""
        # Pop levels that are deeper than our expected level
        while len(indent_stack) > 1 and indent_stack[-1] > expected_indent:
            indent_stack.pop()
        
        # If we're at a different level than expected, adjust
        if indent_stack and indent_stack[-1] != expected_indent:
            indent_stack[-1] = expected_indent

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