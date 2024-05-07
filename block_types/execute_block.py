from .execute_base import execute_base
from CompileError import CompileError
import traceback


class execute_block(execute_base):
    def __init__(self, line, exec_items, sub, else_list=[]):
        self.line = line
        self.exec_items = exec_items
        self.sub = sub
        self.else_list = else_list

    def compile(self, func):
        self.perform_execute(func)

    def display_name(self):
        return "execute"

    def add_continuation_command(self, func, exec_func):
        if len(self.else_list) > 0:
            func.add_command(f"scoreboard players set Global {self.scratch} 1")
            exec_func.add_command(
                f"scoreboard players set Global {self.scratch} 0"
            )

    def force_sub_function(self):
        return len(self.else_list) > 0

    def prepare_scratch(self, func):
        if len(self.else_list) > 0:
            self.scratch = func.get_scratch()

    def compile_else(self, func):
        if len(self.else_list) == 0:
            return

        for idx in range(len(self.else_list)):
            execute_items, else_sub = self.else_list[idx]
            exec_func = func.create_child_function()

            try:
                exec_func.compile_blocks(else_sub)
            except CompileError as e:
                print(e)
                raise CompileError(
                    f"Unable to compile else block contents at line {self.display_name()}"
                )
            except Exception as e:
                print(traceback.format_exc())
                raise CompileError(
                    f"Unable to compile else block contents at line {self.display_name()}"
                )

            if execute_items == None:
                exec_text = ""
            else:
                exec_text = func.get_execute_items(execute_items, exec_func)
            prefix = f"execute if score Global {self.scratch} matches 1.. {exec_text}"
            if idx < len(self.else_list) - 1:
                # There are more else items, so make sure we don't run them
                exec_func.add_command(
                    f"scoreboard players set Global {self.scratch} 0"
                )

            single = exec_func.single_command()
            if single == None:
                unique = func.get_unique_id()
                func_name = f"line{self.line:03}/else{unique}"
                func.register_function(func_name, exec_func)

                func.add_command(f"{prefix}run {exec_func.get_call()}")
            else:
                if single.startswith("/"):
                    single = single[1:]

                cmd = ""

                if single.startswith("$"):
                    single = single[1:]
                    cmd = "$"

                if single.startswith("execute "):
                    cmd = cmd + prefix + single[len("execute ") :]
                else:
                    cmd = cmd + prefix + "run " + single

                func.add_command(cmd)

        func.free_scratch(self.scratch)
