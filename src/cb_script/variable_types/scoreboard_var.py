from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cb_script import mcfunction

from cb_script.variable_types.var_base import var_base


class scoreboard_var(var_base):
    __slots__ = ("selector", "objective")

    def __init__(self, selector: str, objective: str) -> None:
        self.selector = selector
        self.objective = objective

    def get_path(self, func: mcfunction):  # x | None
        if self.selector.startswith("@s"):
            seldef = func.get_self_selector_definition()
        else:
            seldef = func.get_selector_definition(self.selector)

        if seldef is not None:
            if self.objective in seldef.paths:
                return seldef.paths[self.objective]

        return None

    def get_scoreboard_var(self, func: mcfunction, assignto=None):
        """Returns a scoreboard_var for this variable.

        If assignto isn't None, then this function may
        use the assignto objective to opimtize data flow."""
        path_data = self.get_path(func)

        if path_data:
            if assignto is None:
                assignto = scoreboard_var("Global", func.get_scratch())

            assignto.copy_from(func, self)

            return assignto
        else:
            func.register_objective(self.objective)

            name_def = func.get_name_definition(self.selector)
            if name_def is not None:
                return scoreboard_var(name_def, self.objective)

            return self

    def compile(self, func: mcfunction, assignto=None) -> Self:
        name_def = func.get_name_definition(self.selector)
        if name_def is not None:
            return scoreboard_var(name_def, self.objective)
        else:
            return self

    def get_command(self, func: mcfunction) -> str:
        """Returns a command that will get this variable's value to be used with "execute store result"""
        path_data = self.get_path(func)
        if path_data:
            path, data_type, scale = path_data
            return f"data get entity {self.selector} {path} {scale}"
        else:
            func.register_objective(self.objective)

            selector = self.selector
            name_def = func.get_name_definition(self.selector)
            if name_def is not None:
                selector = name_def

            return f"scoreboard players get {selector} {self.objective}"

    # Returns an execute prefix that can be used to set this variable's value when paired with a get_command() command
    def set_command(self, func: mcfunction):
        path_data = self.get_path(func)
        if path_data:
            path, data_type, scale = path_data
            return f"execute store result entity {self.selector} {path} {data_type} {1/float(scale)}"
        else:
            func.register_objective(self.objective)

            selector = self.selector
            name_def = func.get_name_definition(self.selector)
            if name_def is not None:
                selector = name_def

            return f"execute store result score {selector} {self.objective}"

    # Gets a constant integer value for this variable if there is one, otherwise returns None.
    def get_const_value(self, func: mcfunction):
        return None

    def is_objective(self, func: mcfunction, selector: str, objective) -> bool:
        """Returns true if this variable is a scoreboard_var with the specified selector and objective, to reduce extranious copies."""
        path_data = self.get_path(func)

        myselector = self.selector
        name_def = func.get_name_definition(self.selector)
        if name_def is not None:
            myselector = name_def

        if (
            path_data is None
            and myselector == selector
            and self.objective == objective
        ):
            return True
        else:
            return False

    def same_as(self, func: mcfunction, var) -> bool:
        if var is None:
            return False

        myselector = self.selector
        name_def = func.get_name_definition(self.selector)
        if name_def is not None:
            myselector = name_def

        return var.is_objective(func, myselector, self.objective)

    def references_scoreboard_var(self, func: mcfunction, var) -> bool:
        """Returns true if this varariable/expression references the specified scoreboard variable."""
        return self.same_as(func, var)

    def is_fast_selector(self) -> bool:
        if not self.selector.startswith("@"):
            return True

        if self.selector == "@s":
            return True

        return False

    def get_assignto(self, func: mcfunction) -> Self | None:
        """Gets an assignto value for this variable if there is one."""
        path_data = self.get_path(func)
        if path_data is None and self.is_fast_selector():
            func.register_objective(self.objective)

            return self
        else:
            return None

    def copy_from(self, func: mcfunction, var):
        """Copies the value from a target variable to this variable."""
        path_data = self.get_path(func)

        var_const = var.get_const_value(func)

        if path_data:
            path, data_type, scale = path_data

            if var_const is not None:
                suffix = {
                    "byte": "b",
                    "short": "s",
                    "int": "",
                    "long": "L",
                    "float": "f",
                    "double": "d",
                }
                if data_type != "float" and data_type != "double":
                    val = int(var_const / scale)
                else:
                    val = float(var_const) / float(scale)

                func.add_command(
                    f"data modify entity {self.selector} {path} set value {val}{suffix[data_type]}"
                )
            else:
                func.add_command(
                    f"{self.set_command(func)} run {var.get_command(func)}"
                )
        else:
            func.register_objective(self.objective)

            selector = self.selector
            name_def = func.get_name_definition(self.selector)
            if name_def is not None:
                selector = name_def

            if var_const is not None:
                func.add_command(
                    f"scoreboard players set {selector} {self.objective} {var_const}"
                )
            elif not var.is_objective(func, selector, self.objective):
                selvar = var.get_selvar(func)

                if selvar is None:
                    func.add_command(
                        f"{self.set_command(func)} run {var.get_command(func)}"
                    )
                else:
                    func.add_command(
                        f"scoreboard players operation {selector} {self.objective} = {selvar}"
                    )

    # Returns a scoreboard_var which can be modified as needed without side effects
    def get_modifiable_var(self, func: mcfunction, assignto):
        path_data = self.get_path(func)

        if path_data:
            return self.get_scoreboard_var(func, assignto)
        else:
            func.register_objective(self.objective)

            if self.selector == "Global" and func.is_scratch(self.objective):
                return self
            elif self.same_as(func, assignto):
                return self
            else:
                modifiable_var = scoreboard_var("Global", func.get_scratch())
                modifiable_var.copy_from(func, self)

                return modifiable_var

    # If this is a scratch variable, free it up
    def free_scratch(self, func: mcfunction) -> None:
        func.free_scratch(self.objective)

    def uses_macro(self, func: mcfunction) -> bool:
        return (
            func.get_name_definition(self.selector) is not None
            or "$(" in self.selector
        )

    def get_selvar(self, func: mcfunction) -> str | None:
        """Returns the selector and objective of this variable if it is a scoreboard_var, otherwise returns None"""
        path_data = self.get_path(func)
        if path_data:
            return None

        func.register_objective(self.objective)

        name_def = func.get_name_definition(self.selector)

        if name_def is not None:
            return f"{name_def} {self.objective}"
        else:
            return f"{self.selector} {self.objective}"

    @property
    def selvar(self) -> str:
        """This should only be used for scoreboard variables that are known to be Global"""
        return f"{self.selector} {self.objective}"
