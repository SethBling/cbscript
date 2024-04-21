from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from cb_script.CompileError import CompileError

if TYPE_CHECKING:

    from cb_script.global_context import global_context
    from cb_script.mcfunction import mcfunction


class block_base:
    __slots__ = ()

    def compile(self, func: mcfunction):
        raise NotImplementedError("Section does not implement compile()")

    def register(self, global_context: global_context) -> None:
        None

    def compile_lines(self, func: mcfunction, lines):
        try:
            func.compile_blocks(lines)
        except Exception as exc:
            print(exc)
            traceback.print_exception(exc)
            raise CompileError(
                f"Unable to compile {self.block_name} at line {self.line}"
            ) from exc

    @property
    def block_name(self) -> str:
        return "block"
