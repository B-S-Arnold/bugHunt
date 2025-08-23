import ast
from .base_fixer import BaseFixer

class IndentFixer(BaseFixer):
    def fix_code(self, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError:
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
        for each line of code in the node's body and related scopes.
        """
        for child in ast.iter_child_nodes(node):
            if hasattr(child, 'lineno'):
                indent_map[child.lineno] = depth

            for attr in ('body', 'orelse', 'finalbody', 'handlers'):
                if hasattr(child, attr):
                    subnodes = getattr(child, attr)
                    if not isinstance(subnodes, list):
                        subnodes = [subnodes]
                    for subnode in subnodes:
                        if hasattr(subnode, 'lineno'):
                            indent_map[subnode.lineno] = depth + 1
                        self._map_indentation(subnode, depth + 1, indent_map)
