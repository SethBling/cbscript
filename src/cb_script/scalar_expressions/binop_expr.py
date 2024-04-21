from .scalar_expression_base import scalar_expression_base


class binop_expr(scalar_expression_base):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    # Returns true if this varariable/expression references the specified scoreboard variable
    def references_scoreboard_var(self, func, var):
        return self.lhs.references_scoreboard_var(
            func, var
        ) or self.rhs.references_scoreboard_var(func, var)

    def compile(self, func, assignto=None):
        # TODO: Handle case where both variables are constant, and return constant

        if len(self.op) == 1 and self.op in ["+", "-", "*", "/", "%"]:
            left_var = self.lhs.compile(func, assignto)
            left_const = left_var.get_const_value(func)

            right_var = self.rhs.compile(func, None)
            right_const = right_var.get_const_value(func)

            if (
                self.op in ["+", "*"]
                and left_const != None
                and right_const == None
            ):
                # Swap the operands so that the constant is on the right
                old_left_var = left_var
                old_left_const = left_const

                left_var = right_var
                left_const = right_const

                right_var = old_left_var
                right_const = old_left_const

            if assignto != None and not self.rhs.references_scoreboard_var(
                func, assignto
            ):
                assignto.copy_from(func, left_var)
                temp_var = assignto
            else:
                temp_var = left_var.get_modifiable_var(func, assignto)

            # TODO: handle case where both variables have constant values, return constant result

            if right_const and self.op in ["+", "-"]:
                op = self.op

                if right_const < 0:
                    right_const = -right_const
                    op = {"+": "-", "-": "+"}[self.op]

                func.add_command(
                    "scoreboard players {} {} {}".format(
                        {"+": "add", "-": "remove"}[op],
                        temp_var.get_selvar(func),
                        right_const,
                    )
                )
            else:
                right_var = right_var.get_scoreboard_var(func)
                func.add_command(
                    f"scoreboard players operation {temp_var.get_selvar(func)} {self.op}= {right_var.get_selvar(func)}"
                )

            right_var.free_scratch(func)

            return temp_var

        if self.op == "^":
            left_var = self.lhs.compile(func, assignto)
            temp_var = left_var.get_modifiable_var(func, assignto)

            right_var = self.rhs.compile(func)
            power = right_var.get_const_value(func)

            if power == None:
                print("Exponentiation must have constant operand.")
                return None

            power = int(power)

            if power < 1:
                print("Powers less than 1 are not supported")
                return None

            if power == 1:
                return target

            multiplier_obj = func.get_scratch()
            func.add_command(
                f"scoreboard players operation Global {multiplier_obj} = {temp_var.selector} {temp_var.objective}"
            )

            for i in range(power - 1):
                func.add_command(
                    f"scoreboard players operation {temp_var.selector} {temp_var.objective} *= Global {multiplier_obj}"
                )

            func.free_scratch(multiplier_obj)

            return temp_var

        else:
            print(f"Binary operation '{self.op}' isn't implemented")
            return None
