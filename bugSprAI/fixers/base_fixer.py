class BaseFixer:
    def fix_line(self, line: str, line_number: int) -> str:
        raise NotImplementedError

    def fix_code(self, code: str) -> str:
        lines = code.splitlines()
        fixed_lines = [self.fix_line(line, i + 1) for i, line in enumerate(lines)]
        return "\n".join(fixed_lines)

    def set_context(self, known_words: set, logs: list):
        self.known_words = known_words
        self.logs = logs
