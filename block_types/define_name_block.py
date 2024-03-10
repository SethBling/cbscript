from .block_base import block_base

class define_name_block(block_base):
    def __init__(self, line, id, str):
        self.line = line
        self.id = id
        self.str = str[1:-1]

    def compile(self, func):
        func.register_name_definition(self.id, self.str)