from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cb_script.mcfunction import mcfunction


class block_case:
    __slots__ = ("block_name", "lines", "is_default", "props")

    def __init__(
        self,
        block_name: str,
        props: list[tuple[str, str]],
        lines,
        is_default: bool,
    ) -> None:
        self.block_name = block_name
        self.lines = lines
        self.is_default = is_default
        self.props = props

    def matches(self, block: str, state: dict[str, dict[str, str]]) -> bool:
        block_name = self.block_name

        if block_name != "*":
            if not block_name.startswith("minecraft:"):
                block_name = "minecraft:" + block_name

            if block_name != block:
                return False

        if self.props:
            if "properties" not in state:
                return False

            block_props = state["properties"]
            for name, value in self.props:
                if name not in block_props:
                    return False
                if block_props[name] != value:
                    return False

        return True

    def compile(
        self,
        block: str,
        block_state: str,
        block_id: str,
        func: mcfunction,
        falling_block_nbt: str,
    ) -> None:
        func.set_dollarid("block_name", block)
        func.set_dollarid("block_state", block_state)
        func.set_dollarid("block_id", block_id)
        func.set_dollarid("falling_block_nbt", falling_block_nbt)

        func.compile_blocks(self.lines)
