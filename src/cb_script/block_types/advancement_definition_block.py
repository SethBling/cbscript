from cb_script.block_types.block_base import block_base
from cb_script.mcfunction import mcfunction


class advancement_definition_block(block_base):
    def __init__(self, line, name: str, json):
        self.line = line
        self.name = name
        self.json = json

    def compile(self, func: mcfunction) -> None:
        json = func.apply_replacements(self.json)

        func.add_advancement(self.name, json)
