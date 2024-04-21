from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction


from cb_script.block_types.block_base import block_base


class define_name_block(block_base):
    __slots__ = ("id", "str")

    def __init__(self, line: str, id: str, str: str) -> None:
        super().__init__(line)
        self.id = id
        self.str = str[1:-1]

    def compile(self, func: mcfunction) -> None:
        func.register_name_definition(self.id, self.str)
