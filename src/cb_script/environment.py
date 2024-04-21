from __future__ import annotations

import math
from typing import TYPE_CHECKING

from cb_script.CompileError import CompileError
from cb_script.scratch_tracker import scratch_tracker
from cb_script.selector_definition import selector_definition

if TYPE_CHECKING:
    from collections.abc import Buffer
    from typing import Self

    from typing_extensions import SupportsFloat, SupportsIndex

    from cb_script.global_context import global_context as GlobalContext
    from cb_script.mcfunction import mcfunction


def isNumber(s: str | Buffer | SupportsFloat | SupportsIndex) -> bool:
    try:
        val = float(s)

        if math.isinf(val):
            return False

        if math.isnan(val):
            return False

        return True
    except Exception:
        return False


def isInt(s: str | int) -> bool:
    try:
        if isinstance(s, str):
            if s == str(int(s)):
                return True
            return False
        else:
            int(s)
            return True
    except Exception:
        return False


class environment:
    def __init__(self, global_context: GlobalContext) -> None:
        self.dollarid: dict[str, str] = {}
        self.global_context = global_context
        self.scratch = scratch_tracker(global_context)
        self.locals: list[str] = []
        self.selectors: dict[str, selector_definition] = {}
        self.self_selector: selector_definition | None = None
        self.name_definitions: dict[str, str] = {}
        self.pointers: dict[str, str] = {}
        self.block_definitions = {}
        # types: ^^^^^^^^^^^^^
        self.function_name: str | None = None

    def clone(self, new_function_name: str | None = None) -> Self:
        new_env = self.__class__(self.global_context)

        for id_ in self.selectors:
            new_env.selectors[id_] = self.selectors[id_]

        for id_ in self.block_definitions:
            new_env.block_definitions[id_] = self.block_definitions[id_]

        for id_ in self.pointers:
            new_env.pointers[id_] = self.pointers[id_]

        for id_ in self.dollarid:
            new_env.dollarid[id_] = self.dollarid[id_]

        for id_ in self.name_definitions:
            new_env.name_definitions[id_] = self.name_definitions[id_]

        # new_env.dollarid = copy.deepcopy(self.dollarid)
        if new_function_name is None:
            new_env.scratch = self.scratch
            new_env.locals = self.locals
            new_env.function_name = self.function_name
        else:
            new_env.scratch.prefix = self.global_context.get_scratch_prefix(
                new_function_name
            )
            new_env.function_name = new_function_name

        new_env.self_selector = self.self_selector

        return new_env

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_local(self, local) -> None:
        if local not in self.locals:
            self.locals.append(local)

    def apply(self, text: str) -> str:
        text = self.apply_replacements(text)
        text = self.compile_selectors(text)

        return text

    def apply_replacements(
        self, text: str, overrides: dict[str, str] = {}
    ) -> str:
        replacements = {}
        replacements.update(self.dollarid)
        replacements.update(overrides)

        for identifier in sorted(replacements, reverse=True):
            if isInt(replacements[identifier]):
                text = str(text).replace(
                    "-$" + identifier, str(-int(replacements[identifier]))
                )
            elif isNumber(replacements[identifier]):
                text = str(text).replace(
                    "-$" + identifier, str(-float(replacements[identifier]))
                )
            text = str(text).replace(
                "$" + identifier, str(replacements[identifier])
            )

        if text is None:
            raise Exception(
                f'Applying replacements to "{text}" returned None.'
            )

        return text

    def set_dollarid(self, id_: str, val: str) -> None:
        if not id_:
            raise Exception("Dollar ID is empty string.")

        if id_[0] == "$":
            id_ = id_[1:]

        self.dollarid[id_] = val

    def get_dollarid(self, id_: str) -> str:
        if not id_:
            raise Exception("Dollar ID is empty string.")

        id_ = id_.removeprefix("$")

        return self.dollarid[id_]

    def copy_dollarid(self, id_: str, copyid: str) -> None:
        negate = False
        if not id_:
            raise Exception("Dollar ID is empty string.")

        id_ = id_.removeprefix("$")

        if copyid.startswith("$"):
            copyid = copyid[1:]

        if copyid.startswith("-$"):
            copyid = copyid[2:]
            negate = True

        self.dollarid[id_] = self.dollarid[copyid]
        if negate:
            if isInt(self.dollarid[id_]):
                self.dollarid[id_] = str(-int(self.dollarid[id_]))
            elif isNumber(self.dollarid[id_]):
                self.dollarid[id_] = str(-float(self.dollarid[id_]))
            else:
                raise CompileError(
                    f'Unable to negate value of ${copyid} when copying to ${id_}, it has non-numeric value "{self.dollarid[id_]}"'
                )

    def set_atid(self, id_: str, fullselector: str) -> selector_definition:
        self.selectors[id_] = selector_definition(fullselector, self)

        return self.selectors[id_]

    def register_name_definition(self, id_: str, str_: str) -> None:
        self.name_definitions[id_] = str_

    def get_name_definition(self, id_: str) -> str | None:
        if id_ in self.name_definitions:
            return self.name_definitions[id_]
        else:
            return None

    def compile_selectors(self, command: str) -> str:
        ret = ""
        for fragment in self.split_selectors(command):
            if fragment[0] == "@":
                ret = ret + self.compile_selector(fragment)
            else:
                ret = ret + fragment

        return ret

    def get_selector_parts(self, selector: str) -> tuple[str, list[str], str]:
        if len(selector) == 2:
            selector += "[]"

        start = selector[0:3]
        end = selector[-1]
        middle = selector[3:-1]

        parts = middle.split(",")

        return start, [part.strip() for part in parts], end

    def compile_selector(self, selector: str) -> str:
        sel = selector_definition(selector, self)
        interpreted = sel.compile()

        if len(interpreted) == 4:
            # We have @a[] or similar, so truncate
            interpreted = interpreted[:2]

        return interpreted

    def get_python_env(self) -> dict[str, str]:
        return self.dollarid

    def register_objective(self, objective: str) -> None:
        self.global_context.register_objective(objective)

    def split_selectors(self, line: str) -> list[str]:
        fragments = []

        remaining = str(line)
        while "@" in remaining:
            parts = remaining.split("@", 1)
            if len(parts[0]) > 0:
                fragments.append(parts[0])

            end = 0
            for i in range(len(parts[1])):
                if parts[1][i].isalnum() or parts[1][i] == "_":
                    end += 1
                elif parts[1][i] == "[":
                    brack_count = 1
                    for j in range(i + 1, len(parts[1])):
                        if parts[1][j] == "[":
                            brack_count += 1
                        if parts[1][j] == "]":
                            brack_count -= 1
                        if brack_count == 0:
                            end = j + 1
                            break
                    break
                else:
                    break

            fragments.append("@" + parts[1][:end])
            remaining = parts[1][end:]

        if remaining:
            fragments.append(remaining)

        # print(line, fragments)

        return fragments

    def update_self_selector(self, selector: str) -> None:
        if selector[0] != "@":
            return

        id_ = selector[1:]
        if "[" in id_:
            id_ = id_.split("[", 1)[0]

        if id_ in self.selectors:
            self.self_selector = self.selectors[id_]

    def register_array(
        self, name: str, from_val: int, to_val: int, selector_based: bool
    ) -> None:
        self.global_context.register_array(
            name, from_val, to_val, selector_based
        )

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_block_tag(self, name: str, blocks) -> None:
        self.global_context.register_block_tag(name, blocks)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_entity_tag(self, name: str, entities) -> None:
        self.global_context.register_entity_tag(name, entities)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_item_tag(self, name: str, items) -> None:
        self.global_context.register_item_tag(name, items)

    def get_scale(self) -> int:
        # types: no-any-return error: Returning Any from function declared to return "int"
        # types: attr-defined error: "global_context" has no attribute "scale"
        return self.global_context.scale

    # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def set_scale(self, scale: int) -> None:
        # types: attr-defined error: "global_context" has no attribute "scale"
        self.global_context.scale = scale

    # types: ^^^^^^^^^^^^^^^^^^^^^^^^

    scale = property(get_scale, set_scale)

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def arrays(self):
        return self.global_context.arrays

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def block_tags(self):
        return self.global_context.block_tags

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def item_tags(self):
        return self.global_context.item_tags

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def entity_tags(self):
        return self.global_context.entity_tags

    @property
    def namespace(self) -> str:
        return self.global_context.namespace

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def macros(self):
        return self.global_context.macros

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def template_functions(self):
        return self.global_context.template_functions

    @property
    def functions(self) -> dict[str, mcfunction]:
        return self.global_context.functions

    def get_scratch(self) -> str:
        return self.scratch.get_scratch()

    def get_scratch_vector(self) -> list[str]:
        return self.scratch.get_scratch_vector()

    def is_scratch(self, var: str) -> bool:
        return self.scratch.is_scratch(var)

    def free_scratch(self, id_: str) -> None:
        self.scratch.free_scratch(id_)

    def get_temp_var(self) -> str:
        return self.scratch.get_temp_var()

    def free_temp_var(self) -> None:
        # types: call-arg error: Missing positional argument "id_" in call to "free_temp_var" of "scratch_tracker"
        self.scratch.free_temp_var()

    # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def add_constant(self, val: int) -> str:
        return self.global_context.add_constant(val)

    def get_friendly_name(self) -> str:
        return self.global_context.friendly_name

    def get_random_objective(self) -> str:
        return self.global_context.get_random_objective()

    def register_function(self, name: str, func: mcfunction) -> None:
        self.global_context.register_function(name, func)

    def get_unique_id(self) -> int:
        return self.global_context.get_unique_id()

    def register_clock(self, name: str) -> None:
        self.global_context.register_clock(name)

    def get_selector_definition(
        self, selector_text: str
    ) -> selector_definition | None:
        if selector_text.startswith("@"):
            return selector_definition(selector_text, self)
        else:
            return None

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def parser(self):
        return self.global_context.parser

    def register_dependency(self, filename: str) -> None:
        self.global_context.register_dependency(filename)

    def add_pointer(self, block_id: str, selector: str) -> None:
        self.pointers[block_id] = selector

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_block_definition(self, block_id: str, definition) -> None:
        self.block_definitions[block_id] = definition

    # types: no-untyped-def error: Function is missing a return type annotation
    def get_block_definition(self, block_id: str):
        if block_id not in self.block_definitions:
            raise CompileError(f"[{block_id}] is not defined.")

        return self.block_definitions[block_id]

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def get_block_path(
        self,
        func: mcfunction,
        block_id: str,
        path_id: str,
        coords,
        macro_args,
        initialize,
    ) -> tuple[str, str]:
        if block_id not in self.block_definitions:
            raise CompileError(f"[{block_id}] is not defined.")

        if initialize:
            self.block_definitions[block_id].get_path(
                func, path_id, coords, macro_args
            )

        return "Global", path_id

    # types: no-untyped-def error: Function is missing a return type annotation
    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def set_block_path(
        self,
        func: mcfunction,
        block_id: str,
        path_id: str,
        coords,
        macro_args,
        initialize,
    ):
        if block_id not in self.block_definitions:
            raise CompileError(f"[{block_id}] is not defined.")

        self.block_definitions[block_id].set_path(
            func, path_id, coords, macro_args
        )

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_recipe(self, recipe) -> None:
        self.global_context.add_recipe(recipe)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_advancement(self, name: str, advancement) -> None:
        self.global_context.add_advancement(name, advancement)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_loot_table(self, name: str, loot_table) -> None:
        self.global_context.add_loot_table(name, loot_table)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_predicate(self, name: str, predicate) -> None:
        self.global_context.add_predicate(name, predicate)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_item_modifier(self, name: str, item_modifier) -> None:
        self.global_context.add_item_modifier(name, item_modifier)

    # types: no-untyped-def error: Function is missing a return type annotation
    def get_block_state_list(self, include_block_states: bool):
        return self.global_context.get_block_state_list(include_block_states)

    def get_reset_function(self) -> mcfunction | None:
        return self.global_context.get_reset_function()

    def get_all_locals(self) -> list[str]:
        return self.locals + self.scratch.get_active_objectives()

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def predicates(self):
        return self.global_context.predicates
