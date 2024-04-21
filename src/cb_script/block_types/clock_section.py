from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_base import block_base


class clock_section(block_base):
    def __init__(self, line: str, id: str, lines) -> None:
        super().__init__(line)
        self.id = id
        self.lines = lines

    def compile(self, func: mcfunction) -> None:
        clock_func = func.create_child_function(new_function_name=self.id)
        func.register_clock(self.id)
        func.register_function(self.id, clock_func)
        self.compile_lines(clock_func, self.lines)

    @property
    def block_name(self) -> str:
        return f'clock "{self.id}"'
