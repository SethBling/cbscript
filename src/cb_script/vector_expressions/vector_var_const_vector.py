from cb_script.CompileError import CompileError
from cb_script.variable_types.virtualint_var import virtualint_var


class vector_var_const_vector:
    def __init__(self, value):
        self.value = value

    def compile(self, func, assignto):
        components = self.value.get_value(func)

        vars = []
        try:
            vars = [virtualint_var(int(components[i])) for i in range(3)]
        except Exception as e:
            print(e)
            raise CompileError(
                "Unable to get three components from constant vector expression."
            )

        return vars
