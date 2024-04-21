from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cb_script import mcfunction


class var_base:
    """Base class for Minecraft variables. Each variable subclass must implement at least one of the get() functions.

    If the variable is settable, it must implement set_value as well."""

    __slots__ = ()

    def get_scoreboard_var(self, func: mcfunction, assignto=None) -> None:
        """Returns a scoreboard objective for this variable.

        If assignto isn't None, then this function may
        use the assignto objective to opimtize data flow."""
        raise NotImplementedError()

    def get_command(self, func: mcfunction) -> str:
        """Returns a command that will get this variable's value to be used with "execute store result"""
        raise NotImplementedError()

    def get_const_value(self, func: mcfunction):
        """Gets a constant integer value for this variable if there is one, otherwise returns None."""
        return None

    def is_objective(self, func: mcfunction, selector, objective) -> bool:
        """Returns True if this variable is a scoreboard_var with the specified selector and objective, to reduce extranious copies."""
        return False

    def get_assignto(self, func: mcfunction) -> Self | None:
        """Gets an assignto value for this variable if there is one."""
        return None

    def copy_from(self, func: mcfunction, var):
        """Copies the value from a target variable to this variable."""
        raise NotImplementedError()

    def get_modifiable_var(self, func: mcfunction, assignto):
        """Returns a scoreboard_var which can be modified as needed without side effects."""
        raise NotImplementedError()

    def free_scratch(self, func: mcfunction) -> None:
        """If this is a scratch variable, free it up"""
        None

    def get_global_id(self):
        return None

    def get_selvar(self, func: mcfunction) -> str | None:
        """Returns the selector and objective of this variable if it is a scoreboard_var, otherwise returns None."""
        return None

    def references_scoreboard_var(self, func: mcfunction, var) -> bool:
        """Returns true if this varariable/expression references the specified scoreboard variable"""
        return False

    def compile(self, func: mcfunction, assignto=None) -> Self:
        """Used to evaluate a variable as an expression."""
        return self
