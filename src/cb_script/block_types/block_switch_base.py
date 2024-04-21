from cb_script.block_types.block_base import block_base
from cb_script.CompileError import CompileError


class block_switch_base(block_base):
    def __init__(self):
        self.default_case = None
        for case in self.cases:
            if case.is_default:
                if self.default_case:
                    raise CompileError(
                        f"Block switch at line {self.line} has multiple default cases."
                    )
                else:
                    self.default_case = case

        self.block_state_list = {}
        self.block_list = {}
        self.block_state_ids = {}
        self.id_block_states = {}
        self.falling_block_nbt = {}

    # In child classes, can be used to initialize switch variables
    def compile_initialization(self, func):
        None

    # Create and call all required switch/case functions
    def compile(self, func):
        self.compile_initialization(func)
        self.blocks = func.get_block_state_list(
            include_block_states=self.include_block_states
        )
        self.get_block_state_list(func, self.blocks)
        case_ids = self.get_case_ids()

        if self.default_case:
            # If there is a default case, launch right into switch branches
            self.compile_block_cases(func, case_ids)
        else:
            # If there isn't a default case, do initial check on all case ids
            switch_func = func.create_child_function()
            self.compile_block_cases(switch_func, case_ids)
            func.call_function(
                switch_func,
                f"line{self.line:03}/switch_block",
                f"execute if {self.get_range_condition(func, case_ids)} run ",
            )

    # Splits a list into four quartiles
    def get_quartiles(self, list):
        size = len(list)
        return [
            list[: size // 4],
            list[size // 4 : size // 2],
            list[size // 2 : size * 3 // 4],
            list[size * 3 // 4 :],
        ]

    # Creates switch and case function tree
    def compile_block_cases(self, func, block_cases):
        quartiles = self.get_quartiles(block_cases)

        for quartile in quartiles:
            if len(quartile) == 0:
                continue

            if len(quartile) == 1:
                block_case = quartile[0]

                self.compile_block_case(func, block_case)
            else:
                range_func = func.create_child_function()
                self.compile_block_cases(range_func, quartile)

                func.call_function(
                    range_func,
                    f'line{self.line:03}/switch_{str(quartile[0]).replace("minecraft:", "")}-{str(quartile[-1]).replace("minecraft:", "")}',
                    f"execute if {self.get_range_condition(func, quartile)} run ",
                )

    # Gets a block state name in command format from a json block state object
    def get_block_state_name(self, block, state):
        if "properties" in state:
            props = state["properties"]

            return f'{block}[{",".join(f"{p}={props[p]}" for p in props)}]'
        else:
            return block

    # Gets BlockProperties nbt from a json block state object
    def get_falling_block_nbt(self, block, state):
        if "properties" in state:
            props = state["properties"]

            return 'Name:"{}",Properties:{{{}}}'.format(
                block, ",".join(f'{p}:"{props[p]}"' for p in props)
            )

        else:
            return f'Name:"{block}"'

    # Gets a list of all block states matching some case (including the default case)
    def get_block_state_list(self, func, blocks):
        self.block_state_list = {}
        self.block_list = {}

        for block in blocks:
            for state in blocks[block]["states"]:
                block_state = self.get_block_state_name(block, state)

                case = self.get_matching_case(func, block, state)
                if case != None:
                    self.block_state_list[block_state] = case
                    if block not in self.block_list:
                        self.block_list[block] = []
                    self.block_list[block].append(block_state)
                    self.block_state_ids[block_state] = state["id"]
                    self.falling_block_nbt[block_state] = (
                        self.get_falling_block_nbt(block, state)
                    )

        self.id_block_states = {
            self.block_state_ids[block_state]: block_state
            for block_state in self.block_state_ids
        }

    # Finds a case matching a block state in command format
    def get_matching_case(self, func, block, state):
        for case in self.cases:
            if not case.is_default and case.matches(block, state):
                return case

            if (
                not case.is_default
                and case.block_name in func.block_tags
                and block.replace("minecraft:", "")
                in func.block_tags[case.block_name]
            ):
                return case

        return self.default_case
