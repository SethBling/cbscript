from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction
from cb_script.block_types.call_block_base import call_block_base


class function_call_block(call_block_base):
    def __init__(self, line: str, dest, args, with_macro_items) -> None:
        super().__init__(line)
        self.dest, self.args, self.with_macro_items = (
            dest,
            args,
            with_macro_items,
        )

    def compile(self, func: mcfunction) -> None:
        if self.dest == func.name:
            locals = func.get_local_variables()
            func.push_locals(locals)

        self.compile_with_macro_items(func)

        if not func.evaluate_params(self.args):
            raise Exception(
                f"Unable to evaluate function call parameters at line {self.line}"
            )

        cmd = ""

        if ":" in self.dest:
            cmd = f"function {self.dest}"
        else:
            # Default to this datapack's namespace
            cmd = f"function {func.namespace}:{self.dest}"

        if self.with_macro_items is not None:
            cmd += f" with storage {func.namespace}:global args"
            func.has_macros = True

        func.add_command(cmd)

        if self.dest == func.name:
            func.pop_locals(locals)
