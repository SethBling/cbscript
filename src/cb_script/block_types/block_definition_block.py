from cb_script.block_types.block_base import block_base
from cb_script.CompileError import CompileError
from cb_script.mcfunction import mcfunction


class block_definition_block(block_base):
    __slots__ = ("block_id", "items", "coords", "paths")

    def __init__(self, line: str, block_id: str, items, coords) -> None:
        super().__init__(line)
        self.block_id = block_id
        self.items = items
        self.coords = coords
        self.paths = {}

    def compile(self, func: mcfunction) -> None:
        func.add_block_definition(self.block_id, self)

        for item in self.items:
            self.paths[item.get_name()] = item

    def copy_to_objective(
        self, func: mcfunction, path, coords, macro_args, objective: str
    ) -> None:
        if coords is None:
            coords = self.coords

        if path not in self.paths:
            raise CompileError(
                f'No path "{path}" defined for [{self.block_id}].'
            )

        self.paths[id].copy_to_objective(func, coords, macro_args, objective)

    def copy_from(self, func: mcfunction, path, coords, macro_args, var):
        if coords is None:
            coords = self.coords

        if path not in self.paths:
            raise CompileError(
                f'No path "{path}" defined for [{self.block_id}].'
            )

        self.paths[path].copy_from(func, coords, macro_args, var)

    def get_command(self, func: mcfunction, path, coords, macro_args):
        if coords is None:
            coords = self.coords

        if path not in self.paths:
            raise CompileError(
                f'No path "{path}" defined for [{self.block_id}].'
            )

        return self.paths[path].get_command(func, coords, macro_args)
