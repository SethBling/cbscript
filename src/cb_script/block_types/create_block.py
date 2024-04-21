from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_base import block_base


class create_block(block_base):
    __slots__ = ("atid", "relcoords", "index")

    def __init__(self, line: str, atid: str, relcoords, index) -> None:
        super().__init__(line)
        self.atid = atid
        self.relcoords = relcoords
        self.index = index

    def compile(self, func: mcfunction) -> None:
        if not func.run_create(self.atid, self.relcoords, self.index):
            raise Exception(f"Error creating entity at line {self.line}")
