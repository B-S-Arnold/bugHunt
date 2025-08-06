
class BaseFixer:
    def fix_line(self, line: str, line_number: int) -> str:
        raise NotImplementedError

    def set_context(self, known_words: set, logs: list):
        self.known_words = known_words
        self.logs = logs
