import traceback

from cb_script.block_types.block_base import block_base
from cb_script.CompileError import CompileError


class with_anonymous_block(block_base):
    def __init__(self, line, with_items, sub):
        self.line = line
        self.with_items = with_items
        self.sub = sub

    def compile(self, func):
        if self.with_items != None:
            self.with_items.compile(func)

        anon_func = func.create_child_function()

        try:
            anon_func.compile_blocks(self.sub)
        except CompileError as e:
            print(e)
            raise CompileError(
                f"Unable to compile with block contents at line {self.line}"
            )
        except Exception as e:
            print(traceback.format_exc())
            raise CompileError(
                f"Unable to compile with block contents at line {self.line}"
            )

        unique = func.get_unique_id()
        func_name = f'line{self.line:03}/{"with"}{unique:03}'
        func.register_function(func_name, anon_func)

        func.add_command(anon_func.get_call())
