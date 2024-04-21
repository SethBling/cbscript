from .block_base import block_base


class macro_section(block_base):
    def __init__(self, line, name, params, lines):
        self.line = line
        self.name = name
        self.params = params
        self.lines = lines

    def compile(self, func):
        None

    def register(self, global_context):
        global_context.macros[self.name] = (self.params, self.lines)

    @property
    def block_name(self):
        return f'macro "${self.name}"'
