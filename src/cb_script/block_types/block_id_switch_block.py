from __future__ import annotations

from typing import TYPE_CHECKING

from cb_script.CompileError import CompileError

if TYPE_CHECKING:

    from cb_script.mcfunction import mcfunction

from cb_script.block_types.block_switch_base import block_switch_base
from cb_script.CompileError import CompileError


class block_id_switch_block(block_switch_base):
    def __init__(self, line: str, expr, cases, include_block_states) -> None:
        super().__init__(line)
        self.expr = expr
        self.cases = cases
        self.include_block_states = include_block_states

        super().__init__()

    def compile_initialization(self, func: mcfunction) -> None:
        try:
            var = self.expr.compile(func)
            self.condition_var = var.get_scoreboard_var(func)
        except CompileError as exc:
            print(exc)
            traceback.print_exception(exc)
            raise CompileError(
                f"Unable to compile switch expression at line {self.line}."
            ) from exc

    def case_condition(self, block_id: str) -> str:
        return f"score {self.condition_var.selector} {self.condition_var.objective} matches {block_id}"

    def compile_block_case(self, func: mcfunction, id: str) -> None:
        case_func = func.create_child_function()
        block_state = self.id_block_states[id]

        if block_state not in self.block_state_list:
            return

        case = self.block_state_list[block_state]
        falling_block_nbt = self.falling_block_nbt[block_state]

        block = block_state.split("[")[0].replace("minecraft:", "")

        try:
            case.compile(block, block_state, id, case_func, falling_block_nbt)
        except CompileError as e:
            print(e)
            raise CompileError(
                f"Unable to compile block switch at line {self.line}"
            )

        func.call_function(
            case_func,
            f"line{self.line:03}/case{id}",
            f"execute if {self.case_condition(id)} run ",
        )

    def get_range_condition(self, func: mcfunction, ids):
        return f"score {self.condition_var.selector} {self.condition_var.objective} matches {ids[0]}..{ids[-1]}"

    def get_case_ids(self) -> list[str]:
        return sorted(self.id_block_states)
