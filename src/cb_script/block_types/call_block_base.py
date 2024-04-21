from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_base import block_base


class call_block_base(block_base):
    __slots__ = ("with_macro_items",)

    def compile_with_macro_items(self, func: mcfunction) -> None:
        if self.with_macro_items is None:
            return

        self.with_macro_items.compile(func)
