from __future__ import annotations

import json
from typing import TYPE_CHECKING

from cb_script.CompileError import CompileError

if TYPE_CHECKING:
    from cb_script.mcfunction import mcfunction


def get_friendly_name(namespace: str) -> str:
    name = "CB" + namespace[:14]
    name = name.replace(" ", "_")
    name = name.replace(".", "_")
    name = name.replace(",", "_")
    name = name.replace(":", "_")
    name = name.replace("{", "_")
    name = name.replace("}", "_")
    name = name.replace("=", "_")

    return name


def get_constant_name(c: int) -> str:
    if c == -1:
        return "minus"
    elif c >= 0:
        return f"c{c}"
    else:
        return f"cm{-c}"


class global_context:
    def __init__(self, namespace: str) -> None:
        self.clocks: list[str] = []
        self.functions: dict[str, mcfunction] = {}
        # types: var-annotated error: Need type annotation for "function_params" (hint: "function_params: Dict[<type>, <type>] = ...")
        self.function_params = {}
        # types: ^^^^^^^^^^^
        # types: var-annotated error: Need type annotation for "macros" (hint: "macros: Dict[<type>, <type>] = ...")
        self.macros = {}
        # types: ^^
        # types: var-annotated error: Need type annotation for "template_functions" (hint: "template_functions: Dict[<type>, <type>] = ...")
        self.template_functions = {}
        # types: ^^^^^^^^^^^^^^
        self.reset = None
        self.objectives: dict[str, bool] = {}
        self.constants: list[int] = []
        self.arrays: dict[str, tuple[int, int, bool]] = {}
        self.scratch: dict[str, int] = {}
        self.temp = 0
        self.unique = 0
        self.friendly_name = get_friendly_name(namespace)
        # types: var-annotated error: Need type annotation for "block_tags" (hint: "block_tags: Dict[<type>, <type>] = ...")
        self.block_tags = {}
        # types: ^^^^^^
        # types: var-annotated error: Need type annotation for "entity_tags" (hint: "entity_tags: Dict[<type>, <type>] = ...")
        self.entity_tags = {}
        # types: ^^^^^^^
        # types: var-annotated error: Need type annotation for "item_tags" (hint: "item_tags: Dict[<type>, <type>] = ...")
        self.item_tags = {}
        # types: ^^^^^
        # types: var-annotated error: Need type annotation for "scratch_prefixes" (hint: "scratch_prefixes: Dict[<type>, <type>] = ...")
        self.scratch_prefixes = {}
        # types: ^^^^^^^^^^^^
        self.namespace = namespace
        self.parser = None
        self.dependencies: list[str] = []
        # types: var-annotated error: Need type annotation for "recipes" (hint: "recipes: List[<type>] = ...")
        self.recipes = []
        # types: ^^^
        # types: var-annotated error: Need type annotation for "advancements" (hint: "advancements: Dict[<type>, <type>] = ...")
        self.advancements = {}
        # types: ^^^^^^^^
        # types: var-annotated error: Need type annotation for "loot_tables" (hint: "loot_tables: Dict[<type>, <type>] = ...")
        self.loot_tables = {}
        # types: ^^^^^^^
        # types: var-annotated error: Need type annotation for "predicates" (hint: "predicates: Dict[<type>, <type>] = ...")
        self.predicates = {}
        # types: ^^^^^^
        # types: var-annotated error: Need type annotation for "item_modifiers" (hint: "item_modifiers: Dict[<type>, <type>] = ...")
        self.item_modifiers = {}
        # types: ^^^^^^^^^^
        self.block_state_list = None
        self.block_list = None

        # From others
        scale: int = 0

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_block_tag(self, name: str, blocks) -> None:
        self.block_tags[name] = blocks

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_entity_tag(self, name: str, entities) -> None:
        self.entity_tags[name] = entities

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_item_tag(self, name: str, items) -> None:
        self.item_tags[name] = items

    def get_unique_id(self) -> int:
        self.unique += 1
        return self.unique

    def register_clock(self, name: str) -> None:
        self.clocks.append(name)

    def register_function(self, name: str, func: mcfunction) -> None:
        self.functions[name] = func
        func.set_filename(name)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_function_params(self, name: str, params) -> None:
        self.function_params[name] = params

    def register_array(
        self, name: str, from_val: int, to_val: int, selector_based: bool
    ) -> None:
        if name in self.arrays:
            raise CompileError(f'Array "{name}" is defined multiple times.')
        self.arrays[name] = (from_val, to_val, selector_based)

    def register_objective(self, objective: str) -> None:
        if len(objective) > 16:
            raise CompileError(
                f'Cannot create objective "{objective}", name is {len(objective)} characters (max is 16)'
            )
        self.objectives[objective] = True

    def get_reset_function(self) -> mcfunction | None:
        return self.functions.get("reset")

    def add_constant(self, c: str | int) -> str:
        try:
            c = int(c)
        except ValueError as exc:
            print(exc)
            raise Exception(
                f'Unable to create constant integer value for "{c}"'
            ) from exc

        if c not in self.constants:
            self.constants.append(c)

        return get_constant_name(c)

    def add_constant_definitions(self) -> None:
        f = self.get_reset_function()

        if self.constants:
            f.insert_command("/scoreboard objectives add Constant dummy", 0)
            for c in self.constants:
                f.insert_command(
                    f"/scoreboard players set {get_constant_name(c)} Constant {c}",
                    1,
                )

    def allocate_scratch(self, prefix: str, n: int) -> None:
        if prefix not in self.scratch:
            self.scratch[prefix] = 0

        if n > self.scratch[prefix]:
            self.scratch[prefix] = n

    def allocate_temp(self, temp: int) -> None:
        if temp > self.temp:
            self.temp = temp

    def finalize_functions(self) -> None:
        for func in self.functions.values():
            func.finalize()

    def get_scratch_prefix(self, name: str) -> str:
        name = name[:3]
        if name in self.scratch_prefixes:
            i = 2
            while f"{name}{i}" in self.scratch_prefixes:
                i += 1

            name = f"{name}{i}"
            self.scratch_prefixes[name] = True
            return name
        else:
            self.scratch_prefixes[name] = True
            return name

    def get_random_objective(self) -> str:
        return "RV" + self.friendly_name[2:]

    def register_dependency(self, filename: str) -> None:
        self.dependencies.append(filename)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_recipe(self, recipe) -> None:
        self.recipes.append(recipe)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_advancement(self, name: str, advancement) -> None:
        self.advancements[name] = advancement

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_loot_table(self, name: str, loot_table) -> None:
        self.loot_tables[name] = loot_table

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_predicate(self, name: str, predicate) -> None:
        self.predicates[name] = predicate

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_item_modifier(self, name: str, item_modifier) -> None:
        self.item_modifiers[name] = item_modifier

    # types: no-untyped-def error: Function is missing a return type annotation
    def get_block_state_list(self, include_block_states: bool):
        if include_block_states:
            if self.block_state_list:
                # types: unreachable error: Statement is unreachable
                blocks = self.block_state_list
            # types: ^^^^^^^^^^^^^^^^^^^^^^^^^
            else:
                with open("blocks.json") as f:
                    blocks = json.load(f)

                self.block_state_list = blocks

        else:
            if self.block_list:
                # types: unreachable error: Statement is unreachable
                blocks = self.block_list
            # types: ^^^^^^^^^^^^^^^^^^^
            else:
                with open("blocks.json") as f:
                    blocks = json.load(f)

                for id_, block in enumerate(blocks):
                    blocks[block]["states"] = [
                        state
                        for state in blocks[block]["states"]
                        if "default" in state
                    ]
                    if "properties" in blocks[block]["states"][0]:
                        del blocks[block]["states"][0]["properties"]
                    if "properties" in blocks[block]:
                        del blocks[block]["properties"]
                    blocks[block]["states"][0]["id"] = id_

                self.block_list = blocks

        return blocks

    def get_num_blocks(self) -> int:
        blocks = self.get_block_state_list(False)
        return len(blocks)

    def get_num_block_states(self) -> int:
        blocks = self.get_block_state_list(True)
        return len(blocks)
