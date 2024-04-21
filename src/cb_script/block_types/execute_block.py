from __future__ import annotations

from typing import TYPE_CHECKING

from cb_script.CompileError import CompileError

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction
import traceback

from cb_script.block_types.execute_base import execute_base
from cb_script.CompileError import CompileError


class execute_block(execute_base):
    def __init__(
        self, line: str, exec_items, sub, else_list: list = []
    ) -> None:
        super().__init__(line)
        self.exec_items = exec_items
        self.sub = sub
        self.else_list = else_list

    def compile(self, func: mcfunction) -> None:
        self.perform_execute(func)

    def display_name(self) -> str:
        return "execute"

    def add_continuation_command(
        self, func: mcfunction, exec_func: mcfunction
    ) -> None:
        if self.else_list:
            func.add_command(f"scoreboard players set Global {self.scratch} 1")
            exec_func.add_command(
                f"scoreboard players set Global {self.scratch} 0"
            )

    def force_sub_function(self) -> bool:
        return len(self.else_list) > 0

    def prepare_scratch(self, func: mcfunction) -> None:
        if self.force_sub_function():
            self.scratch = func.get_scratch()

    def compile_else(self, func: mcfunction) -> None:
        if not self.else_list:
            return

        for idx, (execute_items, else_sub) in enumerate(self.else_list):
            exec_func = func.create_child_function()

            try:
                exec_func.compile_blocks(else_sub)
            except CompileError as exc:
                print(exc)
                traceback.print_exception(exc)
                raise CompileError(
                    f"Unable to compile else block contents at line {self.display_name()}"
                ) from exc

            if execute_items is None:
                exec_text = ""
            else:
                exec_text = func.get_execute_items(execute_items, exec_func)
            prefix = f"execute if score Global {self.scratch} matches 1.. {exec_text}"
            if idx < len(self.else_list) - 1:
                # There are more else items, so make sure we don't run them
                exec_func.add_command(
                    f"scoreboard players set Global {self.scratch} 0"
                )

            single = exec_func.single_command()
            if single is None:
                unique = func.get_unique_id()
                func_name = f"line{self.line:03}/else{unique}"
                func.register_function(func_name, exec_func)

                func.add_command(f"{prefix}run {exec_func.get_call()}")
            else:
                if single.startswith("/"):
                    single = single[1:]

                cmd = ""

                if single.startswith("$"):
                    single = single[1:]
                    cmd = "$"

                if single.startswith("execute "):
                    cmd = cmd + prefix + single[len("execute ") :]
                else:
                    cmd = cmd + prefix + "run " + single

                func.add_command(cmd)

        func.free_scratch(self.scratch)
