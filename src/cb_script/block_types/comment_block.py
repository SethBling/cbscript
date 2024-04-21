from __future__ import annotations

from cb_script.block_types.command_block import command_block


class comment_block(command_block):
    __slots__ = ()

    def __init__(self, line: str, text: str) -> None:
        super().__init__(line, text)
        if text[0] != "#":
            raise Exception('Comment does not begin with "#"')
