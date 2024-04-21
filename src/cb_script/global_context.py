from CompileError import CompileError
import json


def get_friendly_name(namespace):
    name = "CB" + namespace[:14]
    name = name.replace(" ", "_")
    name = name.replace(".", "_")
    name = name.replace(",", "_")
    name = name.replace(":", "_")
    name = name.replace("{", "_")
    name = name.replace("}", "_")
    name = name.replace("=", "_")

    return name


def get_constant_name(c):
    if c == -1:
        return "minus"
    elif c >= 0:
        return f"c{c}"
    else:
        return f"cm{-c}"


class global_context(object):
    def __init__(self, namespace):
        self.clocks = []
        self.functions = {}
        self.function_params = {}
        self.macros = {}
        self.template_functions = {}
        self.reset = None
        self.objectives = {}
        self.constants = []
        self.arrays = {}
        self.scratch = {}
        self.temp = 0
        self.unique = 0
        self.friendly_name = get_friendly_name(namespace)
        self.block_tags = {}
        self.entity_tags = {}
        self.item_tags = {}
        self.scratch_prefixes = {}
        self.namespace = namespace
        self.parser = None
        self.dependencies = []
        self.recipes = []
        self.advancements = {}
        self.loot_tables = {}
        self.predicates = {}
        self.item_modifiers = {}
        self.block_state_list = None
        self.block_list = None

    def register_block_tag(self, name, blocks):
        self.block_tags[name] = blocks

    def register_entity_tag(self, name, entities):
        self.entity_tags[name] = entities

    def register_item_tag(self, name, items):
        self.item_tags[name] = items

    def get_unique_id(self):
        self.unique += 1
        return self.unique

    def register_clock(self, name):
        self.clocks.append(name)

    def register_function(self, name, func):
        self.functions[name] = func
        func.set_filename(name)

    def register_function_params(self, name, params):
        self.function_params[name] = params

    def register_array(self, name, from_val, to_val, selector_based):
        if name in self.arrays:
            raise CompileError(f'Array "{name}" is defined multiple times.')
        self.arrays[name] = (from_val, to_val, selector_based)

    def register_objective(self, objective):
        if len(objective) > 16:
            raise CompileError(
                f'Cannot create objective "{objective}", name is {len(objective)} characters (max is 16)'
            )
        self.objectives[objective] = True

    def get_reset_function(self):
        if "reset" in self.functions:
            return self.functions["reset"]
        else:
            return None

    def add_constant(self, c):
        try:
            c = int(c)
        except:
            print(e)
            raise Exception(
                f'Unable to create constant integer value for "{c}"'
            )

        if c not in self.constants:
            self.constants.append(c)

        return get_constant_name(c)

    def add_constant_definitions(self):
        f = self.get_reset_function()

        if len(self.constants) > 0:
            f.insert_command("/scoreboard objectives add Constant dummy", 0)
            for c in self.constants:
                f.insert_command(
                    f"/scoreboard players set {get_constant_name(c)} Constant {c}",
                    1,
                )

    def allocate_scratch(self, prefix, n):
        if prefix not in self.scratch:
            self.scratch[prefix] = 0

        if n > self.scratch[prefix]:
            self.scratch[prefix] = n

    def allocate_temp(self, temp):
        if temp > self.temp:
            self.temp = temp

    def finalize_functions(self):
        for func in self.functions.values():
            func.finalize()

    def get_scratch_prefix(self, name):
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

    def get_random_objective(self):
        return "RV" + self.friendly_name[2:]

    def register_dependency(self, filename):
        self.dependencies.append(filename)

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def add_advancement(self, name, advancement):
        self.advancements[name] = advancement

    def add_loot_table(self, name, loot_table):
        self.loot_tables[name] = loot_table

    def add_predicate(self, name, predicate):
        self.predicates[name] = predicate

    def add_item_modifier(self, name, item_modifier):
        self.item_modifiers[name] = item_modifier

    def get_block_state_list(self, include_block_states):
        if include_block_states:
            if self.block_state_list:
                blocks = self.block_state_list
            else:
                with open("blocks.json", "r") as f:
                    blocks = json.load(f)

                self.block_state_list = blocks

        else:
            if self.block_list:
                blocks = self.block_list
            else:
                with open("blocks.json", "r") as f:
                    blocks = json.load(f)

                id = 0
                for block in blocks:
                    blocks[block]["states"] = [
                        state
                        for state in blocks[block]["states"]
                        if "default" in state
                    ]
                    if "properties" in blocks[block]["states"][0]:
                        del blocks[block]["states"][0]["properties"]
                    if "properties" in blocks[block]:
                        del blocks[block]["properties"]
                    blocks[block]["states"][0]["id"] = id
                    id += 1

                self.block_list = blocks

        return blocks

    def get_num_blocks(self):
        blocks = self.get_block_state_list(False)
        return len(blocks)

    def get_num_block_states(self):
        blocks = self.get_block_state_list(True)
        return len(blocks)
