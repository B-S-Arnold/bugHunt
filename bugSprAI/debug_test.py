import ast

class DebugFormatFixer:
    def __init__(self):
        self.used_ast = False

    def fix_code(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            self.used_ast = True
            formatted = ast.unparse(tree)
            print("✓ AST parsing succeeded")
            return self._final_format_pass(formatted)
        except SyntaxError as e:
            print(f"✗ AST parsing failed: {e}")
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
        """Debug version with step-by-step output"""
        print("\n=== FALLBACK FORMATTER DEBUG ===")
        lines = code.splitlines()
        if not lines:
            return code
            
        fixed_lines = []
        indent_level = 0  # Current indentation level (in increments of 4)
        
        block_starters = {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 
            'try', 'except', 'finally', 'with', 'match', 'case'
        }
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            print(f"\nLine {i+1}: {repr(line)} -> stripped: {repr(stripped)}")
            print(f"  Current indent_level: {indent_level}")
            
            if not stripped:
                fixed_lines.append('')
                print(f"  Empty line -> added empty line")
                continue
            
            first_word = stripped.split()[0] if stripped else ''
            print(f"  First word: {repr(first_word)}")
            
            # Special handling for except/finally - they should align with try
            if first_word in ('except', 'finally'):
                try_indent_level = self._find_try_block_indent(fixed_lines)
                current_indent = try_indent_level * 4
                print(f"  EXCEPT/FINALLY: found try at level {try_indent_level}")
                print(f"  Setting current_indent = {current_indent}")
                
                if not stripped.endswith(':'):
                    stripped += ':'
                    print(f"  Added colon: {repr(stripped)}")
                
                indent_level = try_indent_level + 1
                print(f"  Next lines will be at indent_level = {indent_level}")
                
            # Special handling for elif/else - they should align with if
            elif first_word in ('elif', 'else'):
                if_indent_level = self._find_if_block_indent(fixed_lines)
                current_indent = if_indent_level * 4
                print(f"  ELIF/ELSE: found if at level {if_indent_level}")
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = if_indent_level + 1
                
            elif first_word in ('def', 'class'):
                indent_level = 0
                current_indent = 0
                print(f"  DEF/CLASS: setting to level 0")
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level = 1
                print(f"  Next lines will be at indent_level = {indent_level}")
                
            elif first_word in block_starters:
                current_indent = indent_level * 4
                print(f"  BLOCK STARTER: using current indent_level {indent_level} -> {current_indent} spaces")
                
                if not stripped.endswith(':'):
                    stripped += ':'
                
                indent_level += 1
                print(f"  Next lines will be at indent_level = {indent_level}")
                
            else:
                current_indent = indent_level * 4
                print(f"  REGULAR STATEMENT: using indent_level {indent_level} -> {current_indent} spaces")
            
            final_line = ' ' * current_indent + stripped
            fixed_lines.append(final_line)
            print(f"  Final line: {repr(final_line)}")
        
        result = '\n'.join(fixed_lines)
        print(f"\n=== FINAL RESULT ===")
        print(repr(result))
        return result

    def _find_try_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching try statement"""
        print(f"    Searching for try block in previous lines...")
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0]
                print(f"      Checking line: {repr(line)}, first_word: {repr(first_word)}")
                if first_word == 'try':
                    spaces = len(line) - len(line.lstrip())
                    level = spaces // 4
                    print(f"      Found try with {spaces} spaces = level {level}")
                    return level
        print(f"      No try block found, returning 0")
        return 0

    def _find_if_block_indent(self, previous_lines: list) -> int:
        """Find the indentation level (in increments of 4) of the matching if statement"""
        for line in reversed(previous_lines):
            stripped = line.strip()
            if stripped:
                first_word = stripped.split()[0]
                if first_word in ('if', 'elif'):
                    spaces = len(line) - len(line.lstrip())
                    return spaces // 4
        return 0

# Test it
def test_debug():
    buggy_code = '''def list_files(path="."):
        try:
        return os.listdir(path)
except FileNotFoundError:
        return []'''
    
    print("=== TESTING DEBUG FORMATTER ===")
    print("Original code:")
    print(repr(buggy_code))
    print("\nOriginal formatted:")
    print(buggy_code)
    
    formatter = DebugFormatFixer()
    result = formatter.fix_code(buggy_code)
    
    print("\n=== FORMATTED RESULT ===")
    print(result)
    
    print("\n=== EXPECTED ===")
    expected = '''def list_files(path="."):
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return []'''
    print(expected)
    
    print(f"\nMatch? {result.strip() == expected.strip()}")

if __name__ == "__main__":
    test_debug()