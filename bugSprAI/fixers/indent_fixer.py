import ast
import textwrap
from .base_fixer import BaseFixer

class IndentFixer(BaseFixer):
    def fix_code(self, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If AST parsing fails, fall back to original code
            return code

        indent_map = {}
        self._map_indentation(tree, depth=0, indent_map=indent_map)

        fixed_lines = []
        lines = code.splitlines()

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                fixed_lines.append("")
                continue

            depth = indent_map.get(i, 0)
            fixed_lines.append(" " * (depth * 4) + stripped)

        return "\n".join(fixed_lines)

    def _map_indentation(self, node, depth: int, indent_map: dict):
        """
        Recursively walk AST and record indentation depth
        for each line of code in the node's body.
        """
        for child in ast.iter_child_nodes(node):
            if hasattr(child, 'lineno'):
                indent_map[child.lineno] = depth

            if hasattr(child, 'body'):
                for subnode in child.body:
                    if hasattr(subnode, 'lineno'):
                        indent_map[subnode.lineno] = depth + 1
                self._map_indentation(child, depth + 1, indent_map)

            for attr in ('orelse', 'finalbody', 'handlers'):
                if hasattr(child, attr):
                    subbody = getattr(child, attr)
                    if isinstance(subbody, list):
                        for subnode in subbody:
                            if hasattr(subnode, 'lineno'):
                                indent_map[subnode.lineno] = depth + 1
                            self._map_indentation(subnode, depth + 1, indent_map)
                    elif isinstance(subbody, ast.ExceptHandler):
                        if hasattr(subbody, 'lineno'):
                            indent_map[subbody.lineno] = depth + 1
                        self._map_indentation(subbody, depth + 1, indent_map)
