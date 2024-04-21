from cb_script.block_types.block_switch_base import block_switch_base
from cb_script.CompileError import CompileError


class block_id_switch_block(block_switch_base):
    def __init__(self, line, expr, cases, include_block_states):
        self.line = line
        self.expr = expr
        self.cases = cases
        self.include_block_states = include_block_states

        super().__init__()

    def compile_initialization(self, func):
        try:
            var = self.expr.compile(func)
            self.condition_var = var.get_scoreboard_var(func)
        except CompileError as e:
            print(e)
            raise CompileError(
                f"Unable to compile switch expression at line {self.line}."
            )

    def case_condition(self, block_id):
        return f"score {self.condition_var.selector} {self.condition_var.objective} matches {block_id}"

    def compile_block_case(self, func, id):
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

    def get_range_condition(self, func, ids):
        return f"score {self.condition_var.selector} {self.condition_var.objective} matches {ids[0]}..{ids[-1]}"

    def get_case_ids(self):
        return sorted(self.id_block_states.keys())
