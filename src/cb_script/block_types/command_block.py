from .block_base import block_base


class command_block(block_base):
    def __init__(self, line, text):
        self.line = line
        self.text = text

    def compile(self, func):
        func.add_command(self.text)
