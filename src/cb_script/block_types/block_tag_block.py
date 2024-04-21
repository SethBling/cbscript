from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_base import block_base


class block_tag_block(block_base):
    def __init__(self, line: str, name: str, blocks) -> None:
        super().__init__(line)
        self.name = name
        self.blocks = blocks

    def compile(self, func: mcfunction) -> None:
        func.register_block_tag(self.name, self.blocks)
