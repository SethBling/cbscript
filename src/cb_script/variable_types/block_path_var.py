from cb_script.variable_types.scoreboard_var import scoreboard_var
from cb_script.variable_types.var_base import var_base


class block_path_var(var_base):
    def __init__(self, block_id, path_name, coords, macro_args):
        self.block_id = block_id
        self.path_name = path_name
        self.coords = coords
        self.macro_args = macro_args

    # Returns a scoreboard objective for this variable.
    # If assignto isn't None, then this function may
    # use the assignto objective to opimtize data flow.
    def get_scoreboard_var(self, func, assignto=None):
        block_def = func.get_block_definition(self.block_id)

        if assignto == None:
            assignto = scoreboard_var("Global", func.get_scratch())

        func.add_command(
            f"execute store result score {assignto.get_selvar(func)} run {self.get_command(func)}"
        )

        return assignto

    # Returns a command that will get this variable's value to be used with "execute store result"
    def get_command(self, func):
        block_def = func.get_block_definition(self.block_id)
        return block_def.get_command(
            func, self.path_name, self.coords, self.macro_args
        )

    # Copies the value from a target variable to this variable
    def copy_from(self, func, var):
        block_def = func.get_block_definition(self.block_id)
        block_def.copy_from(
            func, self.path_name, self.coords, self.macro_args, var
        )

        var.free_scratch(func)

    # Returns a scoreboard_var which can be modified as needed without side effects
    def get_modifiable_var(self, func, assignto):
        scratch_var = scoreboard_var("Global", func.get_scratch())
        scratch_var.copy_from(func, self)
        return scratch_var
