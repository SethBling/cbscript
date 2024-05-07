class block_case(object):
    def __init__(self, block_name, props, lines, is_default):
        self.block_name = block_name
        self.lines = lines
        self.is_default = is_default
        self.props = props

    def matches(self, block, state):
        block_name = self.block_name

        if block_name != "*":
            if not block_name.startswith("minecraft:"):
                block_name = "minecraft:" + block_name

            if block_name != block:
                return False

        if len(self.props) > 0:
            if "properties" not in state:
                return False

            block_props = state["properties"]
            for name, value in self.props:
                if name not in block_props:
                    return False
                if block_props[name] != value:
                    return False

        return True

    def compile(self, block, block_state, block_id, func, falling_block_nbt):
        func.set_dollarid("block_name", block)
        func.set_dollarid("block_state", block_state)
        func.set_dollarid("block_id", block_id)
        func.set_dollarid("falling_block_nbt", falling_block_nbt)

        func.compile_blocks(self.lines)
