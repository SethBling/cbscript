class vector_binop_base:
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def compile(self, func, assignto):
        return_components = []

        left_component_vars = self.lhs.compile(func, assignto)
        if left_component_vars == None:
            return None

        for i in range(3):
            return_components.append(
                left_component_vars[i].get_modifiable_var(
                    func, assignto[i] if assignto else None
                )
            )

        self.calc_op(func, return_components)

        return return_components
