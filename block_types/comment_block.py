from .block_base import block_base


class comment_block(block_base):
    def __init__(self, line, text):
        self.line = line
        self.text = text
        if text[0] != "#":
            raise Exception('Comment does not begin with "#"')

    def compile(self, func):
        func.add_command(self.text)
