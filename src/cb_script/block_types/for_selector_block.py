import traceback

from cb_script.block_types.block_base import block_base
from cb_script.CompileError import CompileError


class for_selector_block(block_base):
    def __init__(self, line, id, selector, sub):
        self.line = line
        self.id = id
        self.selector = selector
        self.sub = sub

    def compile(self, func):
        scratch_id = func.get_scratch()

        exec_func = func.create_child_function()

        combined_selector = func.get_combined_selector(self.selector)
        combined_selector.scores_min[scratch_id] = 1
        combined_selector.set_part("limit", "1")
        exec_func.selectors[self.id] = combined_selector
        exec_func.update_self_selector(self.selector)

        func.add_command(
            f"scoreboard players set {self.selector} {scratch_id} 0"
        )
        exec_func.add_command(f"scoreboard players set @s {scratch_id} 1")

        try:
            exec_func.compile_blocks(self.sub)
        except CompileError as e:
            print(e)
            raise CompileError(
                f"Unable to compile for block contents at line {self.line}"
            )
        except:
            print(traceback.format_exc())
            raise CompileError(
                f"Unable to compile for block contents at line {self.line}"
            )

        exec_func.add_command(f"scoreboard players set @s {scratch_id} 0")

        func.free_scratch(scratch_id)

        unique = func.get_unique_id()
        exec_name = f"for{unique}_ln{self.line}"
        func.register_function(exec_name, exec_func)

        func.add_command(
            f"execute as {self.selector} run {exec_func.get_call()}"
        )
