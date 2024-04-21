from cb_script.block_types.block_base import block_base


class print_block(block_base):
    def __init__(self, line, val):
        self.line = line
        self.val = val

    def compile(self, func):
        try:
            print(self.val.get_value(func))
        except Exception as e:
            raise Exception(
                f'Unable to get print value at line {self.line}. Exception: "{e}"'
            )
