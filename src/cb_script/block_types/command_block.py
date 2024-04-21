from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_base import block_base


class command_block(block_base):
    __slots__ = ("text",)

    def __init__(self, line: str, text: str) -> None:
        super().__init__(line)
        self.text = text

    def compile(self, func: mcfunction) -> None:
        func.add_command(self.text)
