from cb_script.block_types.block_base import block_base


class scoreboard_assignment_block(block_base):
    def __init__(self, line, var, op, expr):
        self.var, self.op, self.expr = var, op, expr
        self.line = line

    def compile(self, func):
        op = self.op

        if op == "=":
            assignto = self.var.get_assignto(func)
        else:
            assignto = None

        expr_var = self.expr.compile(func, assignto)

        if op == "=":
            self.var.copy_from(func, expr_var)
        else:
            temp_var = self.var.get_scoreboard_var(func)
            expr_const = expr_var.get_const_value(func)

            if expr_const != None and op in ["+=", "-="]:
                if expr_const < 0:
                    expr_const = -expr_const
                    op = {"+=": "-=", "-=": "+="}[op]

                func.add_command(
                    "scoreboard players {} {} {} {}".format(
                        {"+=": "add", "-=": "remove"}[op],
                        temp_var.selector,
                        temp_var.objective,
                        expr_const,
                    )
                )
            else:
                expr_scoreboard_var = expr_var.get_scoreboard_var(func)
                func.add_command(
                    f"scoreboard players operation {temp_var.selector} {temp_var.objective} {self.op} {expr_scoreboard_var.selector} {expr_scoreboard_var.objective}"
                )

                expr_scoreboard_var.free_scratch(func)

            self.var.copy_from(func, temp_var)

            temp_var.free_scratch(func)

        expr_var.free_scratch(func)
