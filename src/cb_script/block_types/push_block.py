from cb_script.block_types.block_base import block_base
from cb_script.variable_types.storage_path_var import storage_path_var


class push_block(block_base):
    def __init__(self, line, expr_list):
        self.expr_list = expr_list
        self.line = line

    def compile(self, func):
        func.add_command(
            f"data modify storage {func.namespace} stack append value {{}}"
        )

        idx = 0
        for expr in self.expr_list:
            expr_var = expr.compile(func)
            data_var = storage_path_var(None, f"stack[-1].v{idx}")
            data_var.copy_from(func, expr_var)

            idx += 1
