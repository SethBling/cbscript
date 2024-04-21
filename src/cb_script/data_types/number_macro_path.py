from cb_script.CompileError import CompileError


class number_macro_path(object):
    def __init__(self, id, params, path, type, scale=None):
        self.id = id
        self.params = params
        self.path = path
        self.type = type
        self.scale = scale

    def get_scale(self, func):
        if self.scale == None:
            scale = func.scale
        else:
            scale = self.scale.get_value(func)

        return scale

    def get_path(self, func, macro_args):
        if len(macro_args) != len(self.params):
            raise CompileError(
                f'"[{self.id}].{self.path}" expects {len(self.params)} macro arguments, received {len(macro_args)}.'
            )

        overrides = {}
        for i in range(len(macro_args)):
            overrides[self.params[i]] = macro_args[i].get_value(func)

        return func.apply_replacements(self.path, overrides)

    def copy_to_objective(self, func, coords, macro_args, objective):
        func.add_command(
            f"execute store result score Global {objective} run {self.get_command(func, coords, macro_args)}"
        )

    def copy_from(self, func, coords, macro_args, var):
        const_val = var.get_const_value(func)
        if const_val:
            func.add_command(
                f"data modify block {coords.get_value(func)} {self.get_path(func, macro_args)} set value {float(const_val) / float(self.get_scale(func))}"
            )
        else:
            func.add_command(
                f"execute store result block {coords.get_value(func)} {self.get_path(func, macro_args)} {self.type} {1 / float(self.get_scale(func))} run {var.get_command(func)}"
            )

    def get_command(self, func, coords, macro_args):
        return f"data get block {coords.get_value(func)} {self.get_path(func, macro_args)} {self.get_scale(func)}"

    def get_name(self):
        return self.id
