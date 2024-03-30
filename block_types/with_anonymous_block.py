import traceback
from CompileError import CompileError, Pos
from .block_base import block_base

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
            raise CompileError(f'Unable to compile with block contents at line {self.line}', Pos(self.line)) from e
        except Exception as e:
            raise CompileError(f'Unable to compile with block contents at line {self.line}', Pos(self.line)) from e
        
        unique = func.get_unique_id()
        func_name = f'line{self.line:03}/{"with"}{unique:03}'
        func.register_function(func_name, anon_func)

        func.add_command(anon_func.get_call())
