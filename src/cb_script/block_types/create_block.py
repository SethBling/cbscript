from cb_script.block_types.block_base import block_base


class create_block(block_base):
    def __init__(self, line, atid, relcoords, index):
        self.line = line
        self.atid = atid
        self.relcoords = relcoords
        self.index = index

    def compile(self, func):
        if not func.run_create(self.atid, self.relcoords, self.index):
            raise Exception(f"Error creating entity at line {self.line}")
