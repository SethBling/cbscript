from __future__ import annotations

import os
import time
import traceback
from typing import TYPE_CHECKING

from cb_script import global_context, mcworld
from cb_script.CompileError import CompileError
from cb_script.environment import environment
from cb_script.mcfunction import mcfunction
from cb_script.source_file import source_file

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from cb_script.source_file import source_file as SourceFile


class ParseResult:
    scale: int
    # types: name-defined error: Name "Any" is not defined
    # types: note: Did you forget to import it from "typing"? (Suggestion: "from typing import Any")
    lines: Iterable[Any]
    # types:        ^
    dir: str
    desc: str


class cbscript:
    __slots__ = (
        "source_file",
        "parse",
        "namespace",
        "dependencies",
        "latest_log_file",
        "global_context",
    )

    def __init__(
        self,
        source_file: SourceFile,
        parse_func: Callable[[str], tuple[str, ParseResult] | None],
    ) -> None:
        self.source_file = source_file
        self.parse = parse_func
        self.namespace = self.source_file.get_base_name().split(".")[0].lower()
        # types: var-annotated error: Need type annotation for "dependencies" (hint: "dependencies: List[<type>] = ...")
        self.dependencies = []
        # types: ^^^^^^^^
        self.latest_log_file: SourceFile | None = None

    def log(self, text: str) -> None:
        print(text)

    def log_traceback(self) -> None:
        traceback.print_exc()

    def check_for_update(self) -> None:
        recompile = False
        # It's important to go through all the files, to make sure that if multiple were updated
        # we don't try to compile multiple times
        for file in [self.source_file] + self.dependencies:
            if file.was_updated():
                recompile = True

        if recompile:
            self.try_to_compile()

        if self.latest_log_file and self.latest_log_file.was_updated():
            log_text = self.latest_log_file.get_text(only_new_text=True)
            self.search_log_for_errors(log_text)

    def search_log_for_errors(self, log_text: str) -> None:
        lines = log_text.splitlines()
        error_text = ""
        for line in lines:
            if len(error_text) == 0:
                # Haven't found an error, keep searching
                if self.namespace in line and (
                    "ERROR" in line or "Exception" in line
                ):
                    error_text = line
            else:
                # Append lines to the error message until it's over
                if len(line) > 0 and line[0] == "[":
                    # Error message is over, print and return
                    print(
                        "========= Error detected in Minecraft log file ========="
                    )
                    print(error_text + "\a")
                    print(
                        "========================================================"
                    )
                    return
                else:
                    # Error message continues
                    if not line.startswith("\t"):
                        error_text = error_text + "\n \n" + line

    def try_to_compile(self) -> None:
        try:
            self.log(f"Compiling {self.namespace}...")
            success = self.compile_all()
            if success:
                self.log(f"Script successfully applied at {time.ctime()}.")
            else:
                self.log("Script had compile error(s).\a")
        except SyntaxError as e:
            self.log(str(e) + "\a")
        except CompileError as e:
            self.log(str(e) + "\a")
        except Exception as e:
            self.log(
                "Compiler encountered unexpected error during compilation:\a"
            )
            self.log_traceback()

    def create_world(self, dir: str, namespace: str) -> mcworld.mcworld:
        return mcworld.mcworld(dir, namespace)

    def compile_all(self) -> bool:
        text = self.source_file.get_text()

        result = self.parse(text + "\n")

        if result is None:
            self.log("Unable to parse script.")
            return False

        type_, parsed = result

        if type_ != "program":
            self.log("Script does not contain a full program.")
            return False

        # types: no-untyped-call error: Call to untyped function "global_context" in typed context
        self.global_context = global_context.global_context(self.namespace)
        # types:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "environment" in typed context
        global_environment = environment(self.global_context)
        # types:             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "set_dollarid" in typed context
        global_environment.set_dollarid("namespace", self.namespace)
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "set_dollarid" in typed context
        global_environment.set_dollarid(
            "get_num_blocks", self.global_context.get_num_blocks
        )
        # types: no-untyped-call error: Call to untyped function "set_dollarid" in typed context
        global_environment.set_dollarid(
            "get_num_block_states", self.global_context.get_num_block_states
        )

        # types: operator error: Unsupported right operand type for in ("ParseResult | Any")
        if "scale" not in parsed:
            # types: ^^^^^^^^^^^
            # types: index error: Unsupported target for indexed assignment ("ParseResult | Any")
            parsed["scale"] = 10000
        # types: ^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "set_dollarid" in typed context
        # types: index error: Value of type "ParseResult | Any" is not indexable
        global_environment.set_dollarid("global_scale", parsed["scale"])
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "mcfunction" in typed context
        global_func = mcfunction(global_environment)
        # types:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # types: attr-defined error: "global_context" has no attribute "scale"
        # types: index error: Value of type "ParseResult | Any" is not indexable
        self.global_context.scale = parsed["scale"]
        # types: ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^
        self.global_context.parser = self.parse

        # types: index error: Value of type "ParseResult | Any" is not indexable
        lines = parsed["lines"]
        # types:        ^^^^^^^^^^^^^^^

        # Register macros and template functions
        for line in lines:
            line.register(self.global_context)

        # Compile all lines
        try:
            # types: no-untyped-call error: Call to untyped function "compile_blocks" in typed context
            global_func.compile_blocks(lines)
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        except Exception as e:
            print(e)
            self.dependencies = [
                source_file(d) for d in self.global_context.dependencies
            ]
            return False

        self.post_processing()

        # types: index error: Value of type "ParseResult | Any" is not indexable
        world = self.create_world(parsed["dir"], self.namespace)
        # types:                          ^^^^^^^^^^^^^

        latest_log_filename = world.get_latest_log_file()
        if os.path.exists(latest_log_filename):
            self.latest_log_file = source_file(latest_log_filename)

        world.write_functions(self.global_context.functions)
        # types: no-untyped-call error: Call to untyped function "write_tags" in typed context
        world.write_tags(
            self.global_context.clocks,
            self.global_context.block_tags,
            self.global_context.entity_tags,
            self.global_context.item_tags,
        )
        # types: index error: Value of type "ParseResult | Any" is not indexable
        world.write_mcmeta(parsed["desc"])
        # types:           ^^^^^^^^^^^^^^
        world.write_recipes(self.global_context.recipes)
        world.write_advancements(self.global_context.advancements)
        world.write_loot_tables(self.global_context.loot_tables)
        world.write_predicates(self.global_context.predicates)
        world.write_item_modifiers(self.global_context.item_modifiers)
        world.write_zip()

        self.dependencies = [
            source_file(d) for d in self.global_context.dependencies
        ]

        return True

    def post_processing(self) -> None:
        # types: no-untyped-call error: Call to untyped function "finalize_functions" in typed context
        self.global_context.finalize_functions()
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.add_scratch_objectives()
        self.add_temp_objectives()
        self.add_constants()
        self.add_trigger_objectives()
        self.add_registered_objectives()
        self.add_max_chain_length()
        self.initialize_stack()
        self.initialize_args()

    def add_max_chain_length(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        f = self.global_context.get_reset_function()
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        f.insert_command("/gamerule maxCommandChainLength 1000000000", 0)

    def initialize_stack(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        f = self.global_context.get_reset_function()
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        f.insert_command(
            f"/data modify storage {self.namespace} stack set value []", 0
        )

    def initialize_args(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        f = self.global_context.get_reset_function()
        # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        f.insert_command(
            f"/data modify storage {self.namespace}:global args set value {{}}",
            0,
        )

    def add_scratch_objectives(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        f = self.global_context.get_reset_function()
        # types:    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        for prefix in self.global_context.scratch:
            for i in range(self.global_context.scratch[prefix]):
                f.insert_command(
                    f"/scoreboard objectives add {prefix}_scratch{i} dummy", 0
                )

    def add_temp_objectives(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        f = self.global_context.get_reset_function()
        # types:    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        for t in range(self.global_context.temp):
            f.insert_command(
                f"scoreboard objectives add temp{str(t)} dummy", 0
            )

    def add_constants(self) -> None:
        # types: no-untyped-call error: Call to untyped function "add_constant_definitions" in typed context
        self.global_context.add_constant_definitions()

    # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def add_trigger_objectives(self) -> None:
        None

    def add_registered_objectives(self) -> None:
        # types: no-untyped-call error: Call to untyped function "get_reset_function" in typed context
        reset = self.global_context.get_reset_function()
        # types:        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        defined = reset.defined_objectives()

        for objective in self.global_context.objectives.keys():
            if objective not in defined:
                reset.insert_command(
                    f"/scoreboard objectives add {objective} dummy", 0
                )
