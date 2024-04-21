from cb_script.block_types.block_base import block_base


class nbt_remove_block(block_base):
    def __init__(self, line, path):
        self.line = line
        self.path = path

    def compile(self, func):
        func.add_command(f"data remove {self.path.get_dest_path(func)}")
