from cb_script import tellraw
from cb_script.block_types.block_base import block_base


class tell_block(block_base):
    def __init__(self, line, selector, unformatted):
        self.line = line
        self.selector = selector
        self.unformatted = unformatted

    def compile(self, func):
        text = tellraw.formatJsonText(
            func, func.apply_replacements(self.unformatted)
        )
        command = f"/tellraw {self.selector} {text}"
        func.add_command(command)
