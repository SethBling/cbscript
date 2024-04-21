from __future__ import annotations

import json
import traceback
from typing import TYPE_CHECKING, NamedTuple

from cb_script.block_types.pop_block import pop_block
from cb_script.block_types.push_block import push_block
from cb_script.CompileError import CompileError
from cb_script.selector_definition import selector_definition
from cb_script.source_file import source_file
from cb_script.variable_types.scoreboard_var import scoreboard_var

if TYPE_CHECKING:
    from collections.abc import Buffer, Iterable
    from types import CodeType

    from cb_script.block_types import block_base
    from cb_script.block_types.command_block import command_block
    from cb_script.environment import environment as Environment


def get_undecorated_selector_name(selector: str) -> str:
    if selector.startswith("@"):
        selector = selector[1:]
    selector = selector.split("[")[0]

    return selector


class Section(NamedTuple):
    type: str  # function, reset, clock
    name: str
    # types: name-defined error: Name "Any" is not defined
    # types: note: Did you forget to import it from "typing"? (Suggestion: "from typing import Any")
    template_params: Any
    # types:         ^
    # types: name-defined error: Name "Any" is not defined
    # types: note: Did you forget to import it from "typing"? (Suggestion: "from typing import Any")
    params: Any
    # types: name-defined error: Name "Any" is not defined
    # types: note: Did you forget to import it from "typing"? (Suggestion: "from typing import Any")
    lines: Any


# types:   ^


def compile_section(section: Section, environment: Environment) -> None:
    type_, name, template_params, params, lines = section

    f: mcfunction | None
    if type_ == "function":
        f = mcfunction(environment.clone(new_function_name=name), True, params)
    elif type_ == "reset":
        f = environment.get_reset_function()
        if f is None:
            f = mcfunction(environment.clone(new_function_name=name))
    else:
        f = mcfunction(environment.clone(new_function_name=name))
    assert f is not None

    environment.register_function(name, f)

    if type_ == "clock":
        environment.register_clock(name)

    f.compile_blocks(lines)


def real_command(cmd: str) -> bool:
    return not cmd.startswith("#") and len(cmd) > 0


class mcfunction:
    def __init__(
        self,
        environment: Environment,
        callable: bool = False,
        params: list[str] = [],
    ) -> None:
        self.commands: list[str] = []
        self.environment = environment
        self.params = params
        self.callable = callable
        self.environment_stack: list[Environment] = []
        self.has_macros = False
        self.filename: str | None = None

        for param in params:
            self.register_local(param)

    def set_filename(self, filename: str) -> None:
        self.filename = filename

    def get_call(self) -> str:
        """Returns the command to call this function."""
        if self.filename is None:
            raise CompileError(
                "Tried to call function with no registered filename."
            )

        if self.has_macros:
            return f"function {self.namespace}:{self.filename} with storage {self.namespace}:global args"
        else:
            return f"function {self.namespace}:{self.filename}"

    def evaluate_params(self, params: Iterable) -> bool:
        results = []
        for index, parameter in enumerate(params):
            param_name = f"Param{index}"
            param_var = scoreboard_var("Global", param_name)
            try:
                var = parameter.compile(self, None)
            except Exception as exc:
                print(exc)
                print(f"Unable to compile parameter {index}.")
                return False

            param_var.copy_from(self, var)

        return True

    def get_arrayconst_var(self, name: str, idxval) -> Any:
        return self.environment.get_arrayconst_var(name, idxval)

    # types: no-untyped-def error: Function is missing a type annotation
    def get_if_chain(
        self,
        conditions: list[
            tuple[Literal[selector] | Literal[predicate], str]
            | tuple[Literal[score], tuple[left, str, right]]
            | tuple[
                Literal[vector_equality],
                tuple[tuple[str, Any], tuple[str, Any]],
            ]
            | tuple[Literal[block], tuple[Any, str]]
            | tuple[Literal[nbtpath], Any]
        ],
        iftype: str = "if",
    ) -> bool:
        test = ""
        for type_, val in conditions:
            if type_ == "selector":
                test += f"{iftype} entity {val} "
            elif type_ == "predicate":
                if ":" in val:
                    test += f"{iftype} predicate {val} "
                elif val in self.predicates:
                    test += f"{iftype} predicate {self.namespace}:{val} "
                else:
                    raise CompileError(f'Predicate "{val}" does not exist')
            elif type_ == "score":
                lexpr, op, rexpr = val

                lvar = lexpr.compile(self)
                rvar = rexpr.compile(self)

                lconst = lvar.get_const_value(self)
                rconst = rvar.get_const_value(self)

                if lconst is not None and rconst is not None:
                    result = False
                    # Perform comparison, terminate if-chain if false
                    if op == "=" and lconst == rconst:
                        result = True
                    elif op == ">" and lconst > rconst:
                        result = True
                    elif op == "<" and lconst < rconst:
                        result = True
                    elif op == ">=" and lconst >= rconst:
                        result = True
                    elif op == "<=" and lconst <= rconst:
                        result = True

                    if (
                        iftype == "if"
                        and not result
                        or iftype == "unless"
                        and result
                    ):
                        # Clobber entire if chain
                        return "if score Global unique matches -1 "
                    else:
                        # No modification to the test string is necessary
                        continue

                elif lconst is not None or rconst is not None:
                    # Continue if chain comparing the scoreboard value with numeric range
                    if lconst is not None:
                        sbvar = rvar.get_scoreboard_var(self)
                        const = lconst
                    elif rconst is not None:
                        sbvar = lvar.get_scoreboard_var(self)
                        const = rconst

                    if op == ">":
                        test += f"{iftype} score {sbvar.selector} {sbvar.objective} matches {int(const)+1}.. "
                    if op == ">=":
                        test += f"{iftype} score {sbvar.selector} {sbvar.objective} matches {const}.. "
                    if op == "<":
                        test += f"{iftype} score {sbvar.selector} {sbvar.objective} matches ..{int(const)-1} "
                    if op == "<=":
                        test += f"{iftype} score {sbvar.selector} {sbvar.objective} matches ..{const} "
                    if op == "=":
                        test += f"{iftype} score {sbvar.selector} {sbvar.objective} matches {const} "

                else:
                    # Continue if chain comparing two score values
                    lsbvar = lvar.get_scoreboard_var(self)
                    rsbvar = rvar.get_scoreboard_var(self)

                    test += f"{iftype} score {lsbvar.selector} {lsbvar.objective} {op} {rsbvar.selector} {rsbvar.objective} "

            elif type_ == "vector_equality":
                if iftype == "unless":
                    raise CompileError(
                        'Vector equality may not be used with "unless"'
                    )

                (type1, var1), (type2, var2) = val

                if type1 == "VAR_CONST" and type2 == "VAR_CONST":
                    val1 = var1.get_value(self)
                    val2 = var2.get_value(self)
                    if val1 != val2:
                        # Test fails, clobber entire chain
                        return "if score Global unique matches -1 "
                    else:
                        # Test succeeds, continue with the chain
                        continue
                else:
                    if type1 == "VAR_CONST":
                        # Swap vars so that the constant var is always second
                        temp_type = type1
                        temp_var = var1
                        type1 = type2
                        var1 = var2
                        type2 = temp_type
                        var2 = temp_var

                    const_vals = []
                    if type2 == "VAR_CONST":
                        components = var2.get_value(self)
                        try:
                            const_vals = [int(components[i]) for i in range(3)]
                        except Exception as e:
                            print(e)
                            raise CompileError(
                                "Unable to get three components for constant vector."
                            )

                    for i in range(3):
                        if type1 == "VAR_ID":
                            lvar = scoreboard_var("Global", f"_{var1}_{i}")
                        elif type1 == "SEL_VAR_ID":
                            sel1, selvar1 = var1
                            lvar = scoreboard_var(sel1, f"_{selvar1}_{i}")
                        elif type1 == "VAR_COMPONENTS":
                            lvar = var1[i].get_scoreboard_var(self)

                        if type2 == "VAR_CONST":
                            # types: name-defined error: Name "sco1" is not defined
                            test += f"if score {sel1} {sco1} matches {const_vals[i]} "
                        # types:                      ^
                        else:
                            if type2 == "VAR_ID":
                                rvar = scoreboard_var("Global", f"_{var2}_{i}")
                            elif type2 == "SEL_VAR_ID":
                                sel2, selvar2 = var2
                                rvar = scoreboard_var(sel2, f"_{selvar2}_{i}")
                            elif type2 == "VAR_COMPONENTS":
                                rvar = var2[i].get_scoreboard_var(self)

                        test += f"if score {lvar.selvar} = {rvar.selvar} "

            elif type_ == "block":
                relcoords, block = val
                block = self.apply_environment(block)

                if block in self.block_tags:
                    block = f"#{self.namespace}:{block}"
                else:
                    block = f"minecraft:{block}"

                test += f"{iftype} block {relcoords.get_value(self)} {block} "
            elif type_ == "nbt_path":
                test += f"{iftype} data {val.get_dest_path(self)} "
            else:
                raise ValueError(f'Unknown "if" type: {type_}')

        return test

    # types: no-untyped-def error: Function is missing a type annotation
    def get_execute_items(
        self,
        exec_items: list[
            tuple[Literal[If], str]
            | tuple[Literal[Unless], str]
            | tuple[Literal[As], str]
            | tuple[Literal[On], str]
            | tuple[Literal[AsId], tuple[str, str]]
            | tuple[Literal[AsCreate], tuple[str, Any]]
            | tuple[Literal[Rotated], tuple[str, Any]]
            | tuple[Literal[FacingCoords], Any]
            | tuple[Literal[FacingEntity], str]
            | tuple[Literal[Align], str]
            | tuple[Literal[At], tuple[str | None, Any | None, str | None]]
            | tuple[Literal[AtVector], tuple[Any | None, Any]]
            | tuple[Literal[In], str]
        ],
        exec_func: Self,
    ) -> str | None:
        cmd = ""
        as_count = 0
        for type_, _ in exec_items:
            if type_[:2] == "As":
                as_count += 1

                if as_count >= 2:
                    print(
                        'Execute chain may only contain a single "as" clause.'
                    )
                    return None

        at_vector_count = 0

        for type_, val in exec_items:
            if type_ == "If":
                # types: no-untyped-call error: Call to untyped function "get_if_chain" in typed context
                cmd += self.get_if_chain(val)
            # types:   ^^^^^^^^^^^^^^^^^^^^^^
            if type_ == "Unless":
                # types: no-untyped-call error: Call to untyped function "get_if_chain" in typed context
                cmd += self.get_if_chain(val, "unless")
            # types:   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            elif type_ == "As":
                cmd += f"as {val} "
                exec_func.update_self_selector(val)
            elif type_ == "On":
                cmd += f"on {val} "
                exec_func.update_self_selector("@s")
            elif type_ == "AsId":
                var, attype = val

                sbvar = var.get_scoreboard_var(self)
                selector, id_ = sbvar.selector, sbvar.objective

                if attype is None:
                    psel = "@e"
                else:
                    psel = f"@{attype}"
                if selector[0] == "@":
                    seldef = selector_definition(selector, self.environment)
                    if (
                        seldef.base_name == "s"
                        and self.environment.self_selector is not None
                        and id_ in self.environment.self_selector.pointers
                    ):
                        psel = self.environment.self_selector.pointers[id_]
                    elif id_ in seldef.pointers:
                        psel = seldef.pointers[id_]
                elif selector == "Global":
                    if id_ in self.environment.pointers:
                        psel = self.environment.pointers[id_]

                self.register_objective("_id")
                self.register_objective(id_)

                self.add_command(
                    f"scoreboard players operation Global _id = {selector} {id_}"
                )

                cmd += f"as {psel} if score @s _id = Global _id "

                if attype is not None:
                    exec_func.update_self_selector("@" + attype)
                elif psel != "@e":
                    exec_func.update_self_selector(
                        "@" + get_undecorated_selector_name(psel)
                    )
                else:
                    exec_func.update_self_selector("@s")
            elif type_ == "AsCreate":
                if len(exec_items) > 1:
                    print(
                        '"as create" may not be paired with other execute commands.'
                    )
                    return None
                create_operation = val

                self.register_objective("_age")
                self.add_command(
                    f"scoreboard players set @{create_operation.atid} _age 1"
                )

                create_operation.compile(self)

                self.add_command(
                    f"scoreboard players add @{create_operation.atid} _age 1"
                )
                cmd += f"as @{create_operation.atid}[_age==1,limit=1] "

                exec_func.update_self_selector("@" + create_operation.atid)
            elif type_ == "Rotated":
                cmd += f"rotated as {val} "
            elif type_ == "FacingCoords":
                cmd += f"facing {val.get_value(self)} "
            elif type_ == "FacingEntity":
                cmd += f"facing entity {val} feet "
            elif type_ == "Align":
                cmd += f"align {val} "
            elif type_ == "At":
                selector, relcoords, anchor = val
                if selector is not None:
                    cmd += f"at {selector} "
                if anchor is not None:
                    cmd += f"anchored {anchor} "
                if relcoords is not None:
                    cmd += f"positioned {relcoords.get_value(self)} "
            elif type_ == "AtVector":
                at_vector_count += 1
                if at_vector_count >= 2:
                    print("Tried to execute at multiple vector locations.")
                    return None

                scale, expr = val
                if scale is None:
                    scale = self.scale
                else:
                    scale = scale.get_value(self)

                vec_vals = expr.compile(self, None)
                self.add_command("scoreboard players add @e _age 1")
                self.add_command("summon area_effect_cloud")
                self.add_command("scoreboard players add @e _age 1")
                for i in range(3):
                    var = vec_vals[i].get_scoreboard_var(self)
                    self.add_command(
                        f"execute store result entity @e[_age==1,limit=1] Pos[{i}] double {1/float(scale)} run scoreboard players get {var.selector} {var.objective}"
                    )
                cmd += "at @e[_age == 1] "
                exec_func.add_command("/kill @e[_age == 1]")
            elif type_ == "In":
                dimension = val
                cmd += f"in {dimension} "
            else:
                raise ValueError(f'Unknown "execute_item" type: {type_}')

        return cmd

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def switch_cases(
        self,
        var,
        cases: list[tuple[int, int, list[command_block], str, None]],
        switch_func_name: str = "switch",
        case_func_name: str = "case",
    ) -> bool:
        for q in range(4):
            imin = q * len(cases) // 4
            imax = (q + 1) * len(cases) // 4
            if imin == imax:
                continue

            vmin = cases[imin][0]
            vmax = cases[imax - 1][1]
            line = cases[imin][3]

            sub_cases = cases[imin:imax]
            case_func = self.create_child_function()

            if len(sub_cases) == 1:
                vmin, vmax, sub, line, dollarid = sub_cases[0]
                if dollarid is not None:
                    # types: unreachable error: Statement is unreachable
                    case_func.set_dollarid(dollarid, vmin)
                # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                try:
                    case_func.compile_blocks(sub)
                except CompileError as e:
                    print(e)
                    raise CompileError(
                        f"Unable to compile case at line {line}"
                    )
                except Exception as e:
                    print(traceback.format_exc())
                    raise CompileError(
                        f"Unable to compile case at line {line}"
                    )

                single_command = case_func.single_command()
                if single_command is not None:
                    if vmin == vmax:
                        vrange = str(vmin)
                    else:
                        vrange = f"{vmin}..{vmax}"

                    if len(single_command) >= 1 and single_command[0] == "$":
                        self.add_command(
                            f"$execute if score {var.selector} {var.objective} matches {vrange} run {single_command[1:]}"
                        )
                    else:
                        self.add_command(
                            f"execute if score {var.selector} {var.objective} matches {vrange} run {single_command}"
                        )
                else:
                    unique = self.get_unique_id()

                    if vmin == vmax:
                        case_name = (
                            f"line{line}/{case_func_name}{vmin}_{unique}"
                        )
                    else:
                        case_name = f"line{line}/{case_func_name}{vmin}-{vmax}_{unique}"

                    self.register_function(case_name, case_func)
                    self.add_command(
                        f"execute if score {var.selector} {var.objective} matches {vmin}..{vmax} run {case_func.get_call()}"
                    )
            else:
                unique = self.get_unique_id()
                case_name = (
                    f"line{line}/{switch_func_name}{vmin}-{vmax}_{unique}"
                )
                self.register_function(case_name, case_func)
                self.add_command(
                    f"execute if score {var.selector} {var.objective} matches {vmin}..{vmax} run {case_func.get_call()}"
                )

                if not case_func.switch_cases(var, sub_cases):
                    return False

        return True

    def add_operation(
        self, selector: str, id1: str, operation: str, id2: str
    ) -> None:
        selector = self.environment.apply(selector)

        self.add_command(
            f"scoreboard players operation {selector} {id1} {operation} {selector} {id2}"
        )

        if self.is_scratch(id2):
            self.free_scratch(id2)

    def add_command(self, command: str) -> None:
        self.insert_command(command, len(self.commands))

    def insert_command(self, command: str, index: int) -> None:
        if not command:
            return

        if command[0] != "#":
            if command[0] == "/":
                command = command[1:]

            command = self.environment.apply(command)

            if "$(" in command:
                if command[0] != "$":
                    command = "$" + command

                self.has_macros = True

        self.commands.insert(index, command)

    def get_utf8_text(self) -> bytes:
        return "\n".join(
            (cmd if cmd[0] != "/" else cmd[1:]) for cmd in self.commands
        ).encode("utf-8")

    def defined_objectives(self) -> dict[str, bool]:
        existing: dict[str, bool] = {}
        defineStr = "scoreboard objectives add "
        for cmd in self.commands:
            if cmd[0] == "/":
                cmd = cmd[1:]
            if cmd[: len(defineStr)] == defineStr:
                existing[cmd[len(defineStr) :].split(" ")[0]] = True

        return existing

    def register_local(self, id_: str) -> None:
        self.environment.register_local(id_)

    def finalize(self) -> None:
        comments = []
        while (
            len(self.commands) > 0
            and len(self.commands[0]) >= 2
            and self.commands[0][0:2] == "##"
        ):
            comments.append(self.commands[0])
            del self.commands[0]

        if self.callable:
            for v in self.environment.scratch.get_allocated_variables():
                self.register_local(v)

            for p in range(len(self.params)):
                self.insert_command(
                    f"scoreboard players operation Global {self.params[p]} = Global Param{p}",
                    0,
                )
                self.register_objective(f"Param{p}")

        self.commands = comments + self.commands

    def single_command(self) -> str | None:
        ret = None
        count = 0
        for cmd in self.commands:
            if real_command(cmd):
                ret = cmd
                count += 1

            if count >= 2:
                return None

        return ret

    def is_empty(self) -> bool:
        for cmd in self.commands:
            if real_command(cmd):
                return False

        return True

    def check_single_entity(self, selector: str) -> bool:
        if selector[0] != "@":
            return True

        parsed = self.environment.get_selector_definition(selector)
        if parsed is None:
            raise CompileError(f"Selector {selector!r} does not exist!")
        return parsed.single_entity()

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def get_path(self, selector: str, var) -> None:
        if selector[0] != "@":
            return
        id_ = selector[1:]
        if "[" in id_:
            id_ = id_.split("[", 1)[0]

        if id_ in self.environment.selectors:
            sel_def = self.environment.selectors[id_]
        elif id_ == "s" and self.environment.self_selector is not None:
            sel_def = self.environment.self_selector
        else:
            return

        if var in sel_def.paths:
            path, data_type, scale = sel_def.paths[var]
            if scale is None:
                scale = self.scale

            if not self.check_single_entity(selector):
                raise CompileError(
                    f'Tried to get data "{var}" from selector "{selector}" which is not limited to a single entity.'
                )

            self.add_command(
                f"execute store result score {selector} {var} run data get entity {selector} {path} {scale}"
            )

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def set_path(self, selector: str, var) -> None:
        if selector[0] != "@":
            return
        id_ = selector[1:]
        if "[" in id_:
            id_ = id_.split("[", 1)[0]

        if id_ in self.environment.selectors:
            sel_def = self.environment.selectors[id_]
        elif id_ == "s" and self.environment.self_selector is not None:
            sel_def = self.environment.self_selector
        else:
            return

        if var in sel_def.paths:
            path, data_type, scale = sel_def.paths[var]
            if scale is None:
                scale = self.scale

            if not self.check_single_entity(selector):
                raise CompileError(
                    f'Tried to set data "{var}" for selector "{selector}" which is not limited to a single entity.'
                )

            self.add_command(
                f"execute store result entity {selector} {path} {data_type} {1/float(scale)} run scoreboard players get {selector} {var}"
            )

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def get_vector_path(self, selector: str, var) -> bool:
        if selector[0] != "@":
            return False
        id_ = selector[1:]
        if "[" in id_:
            id_ = id_.split("[", 1)[0]

        if id_ in self.environment.selectors:
            sel_def = self.environment.selectors[id_]
        elif id_ == "s" and self.environment.self_selector is not None:
            sel_def = self.environment.self_selector
        else:
            return False

        if var in sel_def.vector_paths:
            path, data_type, scale = sel_def.vector_paths[var]
            if scale is None:
                scale = self.scale

            if not self.check_single_entity(selector):
                raise CompileError(
                    f'Tried to get vector data "{var}" from selector "{selector}" which is not limited to a single entity.'
                )

            for i in range(3):
                self.add_command(
                    f"execute store result score {selector} _{var}_{i} run data get entity {selector} {path}[{i}] {scale}"
                )

            return True
        else:
            return False

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def set_vector_path(self, selector: str, var, values) -> bool:
        if selector[0] != "@":
            return False
        id_ = selector[1:]
        if "[" in id_:
            id_ = id_.split("[", 1)[0]

        if id_ in self.environment.selectors:
            sel_def = self.environment.selectors[id_]
        elif id_ == "s" and self.environment.self_selector is not None:
            sel_def = self.environment.self_selector
        else:
            return False

        if var in sel_def.vector_paths:
            path, data_type, scale = sel_def.vector_paths[var]
            if scale is None:
                scale = self.scale

            if not self.check_single_entity(selector):
                raise CompileError(
                    f'Tried to set vector data "{var}" for selector "{selector}" which is not limited to a single entity.'
                )

            for i in range(3):
                val_var = values[i].get_scoreboard_var(self)
                self.add_command(
                    f"execute store result entity {selector} {path}[{i}] {data_type} {1/float(scale)} run scoreboard players get {val_var.selector} {val_var.objective}"
                )

            return True
        else:
            return False

    def register_objective(self, objective: str) -> None:
        self.environment.register_objective(objective)

    def register_array(
        self, name: str, from_val: int, to_val: int, selector_based: bool
    ) -> None:
        self.environment.register_array(name, from_val, to_val, selector_based)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def apply_replacements(self, text: str, overrides={}) -> str:
        return self.environment.apply_replacements(text, overrides)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_block_tag(self, name: str, blocks) -> None:
        self.environment.register_block_tag(name, blocks)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_entity_tag(self, name: str, entities) -> None:
        self.environment.register_entity_tag(name, entities)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def register_item_tag(self, name: str, items) -> None:
        self.environment.register_item_tag(name, items)

    def get_scale(self) -> int:
        # types: no-any-return error: Returning Any from function declared to return "int"
        return self.environment.scale

    # types: ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def set_scale(self, scale: int) -> None:
        self.environment.scale = scale

    scale = property(get_scale, set_scale)

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def arrays(self):
        return self.environment.arrays

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def block_tags(self):
        return self.environment.block_tags

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def item_tags(self):
        return self.environment.item_tags

    @property
    def namespace(self) -> str:
        return self.environment.namespace

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def macros(self):
        return self.environment.macros

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def template_functions(self):
        return self.environment.template_functions

    @property
    # types: name-defined error: Name "Self" is not defined
    def functions(self) -> dict[str, Self]:
        # types:                     ^
        return self.environment.functions

    @property
    def selectors(self) -> dict[str, selector_definition]:
        return self.environment.selectors

    def get_scratch(self) -> str:
        return self.environment.get_scratch()

    def get_scratch_vector(self) -> list[str]:
        return self.environment.get_scratch_vector()

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def is_scratch(self, var) -> bool:
        return self.environment.is_scratch(var)

    def free_scratch(self, id_: str) -> None:
        self.environment.free_scratch(id_)

    def get_temp_var(self) -> str:
        return self.environment.get_temp_var()

    def free_temp_var(self) -> None:
        self.environment.free_temp_var()

    def apply_environment(self, text: str) -> str:
        return self.environment.apply(text)

    def add_constant(self, val: int) -> str:
        return self.environment.add_constant(val)

    def get_friendly_name(self) -> str:
        return self.environment.get_friendly_name()

    def get_random_objective(self) -> str:
        return self.environment.get_random_objective()

    # types: name-defined error: Name "Self" is not defined
    def register_function(self, name: str, func: Self) -> None:
        # types:                                 ^
        self.environment.register_function(name, func)

    def get_unique_id(self) -> int:
        return self.environment.get_unique_id()

    def update_self_selector(self, selector: str) -> None:
        self.environment.update_self_selector(selector)

    def get_self_selector_definition(self) -> selector_definition | None:
        return self.environment.self_selector

    def get_python_env(self) -> dict[str, str]:
        return self.environment.get_python_env()

    def clone_environment(
        self, new_function_name: str | None = None
    ) -> Environment:
        return self.environment.clone(new_function_name=new_function_name)

    def get_combined_selector(self, selector: str) -> selector_definition:
        """Combines a selector with an existing selector definition in the environment."""
        return selector_definition(selector, self.environment)

    def set_dollarid(self, id_: str, val: str) -> None:
        self.environment.set_dollarid(id_, val)

    def get_dollarid(self, id_: str) -> str:
        return self.environment.get_dollarid(id_)

    def set_atid(self, id_: str, fullselector: str) -> selector_definition:
        return self.environment.set_atid(id_, fullselector)

    def push_environment(self, new_env: Environment) -> None:
        self.environment_stack.append(self.environment)
        self.environment = new_env

    def pop_environment(self) -> None:
        self.environment = self.environment_stack.pop()

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def run_create(self, atid: str, relcoords, idx=None) -> bool:
        if atid not in self.selectors:
            print(f"Unable to create unknown entity: @{atid}")
            return False

        selector = self.selectors[atid]

        entity_type = selector.get_type()

        if entity_type is None:
            print(f"Unable to create @{atid}, no entity type is defined.")
            return False

        if selector.tag is None:
            if idx:
                self.add_command(
                    f"summon {entity_type} {relcoords.get_value(self)} {idx.get_value(self) + hash(atid) % (2 ** 32)}}}"
                )
            else:
                self.add_command(
                    f"summon {entity_type} {relcoords.get_value(self)}"
                )
        else:
            if idx:
                parsed = json.loads(selector.tag)
                parsed["UUIDMost"] = 0
                parsed["UUIDLeast"] = idx.get_value(self) + hash(atid) % (
                    2**32
                )
                tag = json.dumps(parsed)
            else:
                tag = selector.tag

            self.add_command(
                f"summon {entity_type} {relcoords.get_value(self)} {tag}"
            )

        return True

    def register_name_definition(self, id_: str, str_: str) -> None:
        self.environment.register_name_definition(id_, str_)

    def get_name_definition(self, id_: str) -> str | None:
        return self.environment.get_name_definition(id_)

    def create_child_function(
        self,
        new_function_name: str | None = None,
        callable: bool = False,
        params: list[str] = [],
        # types: name-defined error: Name "Self" is not defined
    ) -> Self:
        """Creates an empty function with a copy of the current environment."""
        return self.__class__(
            self.clone_environment(new_function_name=new_function_name),
            callable=callable,
            params=params,
        )

    # types: valid-type error: Module "cb_script.block_types.block_base" is not valid as a type
    # types: note: Perhaps you meant to use a protocol matching the module structure?
    def compile_blocks(self, lines: Iterable[block_base]) -> None:
        # types:                             ^
        for block in lines:
            try:
                # types: attr-defined error: block_base? has no attribute "compile"
                block.compile(self)
            # types: ^^^^^^^^
            except Exception as exc:
                print(exc)
                traceback.print_exception(exc)
                raise CompileError(
                    # types: attr-defined error: block_base? has no attribute "line"
                    f"Error compiling block at line {block.line}"
                    # types:                            ^^^^^^^^^^^
                ) from exc

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def parser(self):
        return self.environment.parser

    def import_file(self, filename: str) -> None:
        self.environment.register_dependency(filename)

        file = source_file(filename)

        result = self.parser("import " + file.get_text() + "\n")
        if result is None:
            raise CompileError(f'Unable to parse file "{filename}"')

        type_, parsed = result
        if type_ != "lib":
            raise CompileError(f'Unable to import non-lib-file "{filename}"')

        for line in parsed["lines"]:
            line.register(self.global_context)

        self.compile_blocks(parsed["lines"])

    def import_python_file(self, filename: str) -> None:
        self.environment.register_dependency(filename)

        try:
            with open(filename, encoding="utf-8") as file:
                text = file.read()
        except Exception as exc:
            print(exc)
            raise CompileError(f'Unable to open "{filename}"') from exc

        try:
            exec(text, globals(), self.get_python_env())
        except Exception as e:
            print(e)
            raise CompileError(f'Unable to execute "{filename}"')

    # types: no-untyped-def error: Function is missing a return type annotation
    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def eval(self, expr: str | Buffer | CodeType, line):
        try:
            return eval(expr, globals(), self.get_python_env())
        except Exception as exc:
            print(exc)
            raise CompileError(
                f'Could not evaluate python expression "{expr}" at line {line}'
            ) from exc

    def add_pointer(self, id_: str, selector: str) -> None:
        self.environment.add_pointer(id_, selector)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_block_definition(self, id_: str, definition) -> None:
        self.environment.add_block_definition(id_, definition)

    # types: no-untyped-def error: Function is missing a return type annotation
    def get_block_definition(self, block_id: str):
        return self.environment.get_block_definition(block_id)

    def get_selector_definition(
        self, selector: str
    ) -> selector_definition | None:
        return self.environment.get_selector_definition(selector)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_recipe(self, recipe) -> None:
        self.environment.add_recipe(recipe)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_advancement(self, name: str, advancement) -> None:
        self.environment.add_advancement(name, advancement)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_loot_table(self, name: str, loot_table) -> None:
        self.environment.add_loot_table(name, loot_table)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_predicate(self, name: str, predicate) -> None:
        self.environment.add_predicate(name, predicate)

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def add_item_modifier(self, name: str, item_modifier) -> None:
        self.environment.add_item_modifier(name, item_modifier)

    # types: no-untyped-def error: Function is missing a return type annotation
    def get_block_state_list(self, include_block_states: bool):
        return self.environment.get_block_state_list(include_block_states)

    def call_function(
        # types: name-defined error: Name "Self" is not defined
        self,
        sub_func: Self,
        sub_name: str,
        prefix: str = "",
        # types:            ^
    ) -> None:
        if sub_func.is_empty():
            return

        single_command = sub_func.single_command()

        if single_command:
            if single_command.startswith("$"):
                self.add_command(f"${prefix}{single_command[1:]}")
            else:
                self.add_command(f"{prefix}{single_command}")
        else:
            unique = self.get_unique_id()
            sub_name = f"{sub_name}_{unique}"

            self.register_function(sub_name, sub_func)
            cmd = prefix + sub_func.get_call()

            self.add_command(cmd)

    # types: name-defined error: Name "Self" is not defined
    def get_reset_function(self) -> Self | None:
        # types:                    ^
        return self.environment.get_reset_function()

    def register_clock(self, id_: str) -> None:
        self.environment.register_clock(id_)

    @property
    # types: name-defined error: Name "global_context" is not defined
    def global_context(self) -> global_context:
        # types:                ^
        return self.environment.global_context

    # types: name-defined error: Name "Self" is not defined
    def copy_environment_from(self, func: Self) -> None:
        # types:                          ^
        self.environment = func.environment.clone()

    @property
    def name(self) -> str | None:
        return self.environment.function_name

    def get_local_variables(self) -> list[scoreboard_var]:
        return [
            scoreboard_var("Global", l)
            for l in self.environment.get_all_locals()
        ]

    # types: no-untyped-def error: Function is missing a type annotation for one or more arguments
    def push_locals(self, locals_) -> None:
        # types: no-untyped-call error: Call to untyped function "push_block" in typed context
        block = push_block(0, locals_)
        # types: ^^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "compile" in typed context
        block.compile(self)

    # types: ^^^^^^^^^^^^^^^^^^

    # types: no-untyped-def error: Function is missing a type annotation
    def pop_locals(self, locals_):
        # types: no-untyped-call error: Call to untyped function "pop_block" in typed context
        block = pop_block(0, locals_)
        # types: ^^^^^^^^^^^^^^^^^^^^
        # types: no-untyped-call error: Call to untyped function "compile" in typed context
        block.compile(self)

    # types: ^^^^^^^^^^^^^^^^^^

    @property
    # types: no-untyped-def error: Function is missing a return type annotation
    def predicates(self):
        return self.environment.predicates
