from .block_switch_base import block_switch_base
from CompileError import CompileError


class block_switch_block(block_switch_base):
    def __init__(self, line, coords, cases, include_block_states):
        self.line = line
        self.coords = coords
        self.cases = cases
        self.include_block_states = include_block_states

        super(block_switch_block, self).__init__()

    def case_condition(self, func, block_state):
        return f"block {self.coords.get_value(func)} {block_state}"

    def compile_block_case(self, func, block):
        single_case = self.get_matching_case(func, block, {})

        if single_case and not single_case.is_default:
            block_state = block
            if "properties" in self.blocks[block]:
                first = True
                block_state += "["

                props = self.blocks[block]["properties"]
                for prop in props:
                    if first:
                        first = False
                    else:
                        block_state += ","

                    block_state += f"{prop}={props[prop][0]}"

                block_state += "]"

            self.compile_single_case(
                func,
                block,
                block,
                block_state,
                f'line{self.line:03}/case_{block.replace("minecraft:", "")}',
            )
        elif "properties" in self.blocks[block]:
            case_func = func.create_child_function()

            props = self.blocks[block]["properties"]
            self.compile_property_case(
                case_func, block, props.keys(), props, f"{block}["
            )
            func.call_function(
                case_func,
                f'line{self.line:03}/switch_{block.replace("minecraft:", "")}/{block.replace("minecraft:", "")}',
                f"execute if block {self.coords.get_value(func)} {block} run ",
            )
        elif self.default_case:
            self.compile_single_case(
                func,
                block,
                block,
                block,
                f'line{self.line:03}/case_{block.replace("minecraft:", "")}',
            )

    def compile_property_case(
        self, func, block, prop_names, props, partial_block_state
    ):
        cur_prop_name = prop_names[0]
        cur_prop = props[cur_prop_name]

        if len(prop_names) == 1:
            for value in cur_prop:
                block_state = f"{partial_block_state}{cur_prop_name}={value}]"
                if block_state in self.block_state_list:
                    self.compile_single_case(
                        func,
                        block,
                        block_state,
                        block_state,
                        f'line{self.line:03}/switch_{block.replace("minecraft:", "")}/{cur_prop_name}_{value}',
                    )
        else:
            for value in cur_prop:
                block_state = f"{partial_block_state}{cur_prop_name}={value},"

                case_func = func.create_child_function()

                self.compile_property_case(
                    case_func, block, prop_names[1:], props, block_state
                )
                func.call_function(
                    case_func,
                    f'line{self.line:03}/switch_{block.replace("minecraft:", "")}/{cur_prop_name}_{value}',
                    f"execute if block {self.coords.get_value(func)} {block}[{cur_prop_name}={value}] run ",
                )

    def compile_single_case(
        self, func, block, block_test, block_state, case_func_name
    ):
        id = self.block_state_ids[block_state]
        case = self.block_state_list[block_state]
        falling_block_nbt = self.falling_block_nbt[block_state]

        case_func = func.create_child_function()
        try:
            case.compile(
                block.replace("minecraft:", ""),
                block_state,
                id,
                case_func,
                falling_block_nbt,
            )
        except CompileError as e:
            print(e)
            raise CompileError(
                f'Unable to compile block switch case "{block_state}" at line {self.line}'
            )

        func.call_function(
            case_func,
            case_func_name,
            f"execute if {self.case_condition(func, block_test)} run ",
        )

    def get_range_condition(self, func, blocks):
        unique = func.get_unique_id()
        block_tag_name = f"switch_{unique}"
        func.register_block_tag(
            block_tag_name,
            [block.replace("minecraft:", "") for block in blocks],
        )

        return f"block {self.coords.get_value(func)} #{func.namespace}:{block_tag_name}"

    def get_case_ids(self):
        return sorted(self.block_list.keys())
