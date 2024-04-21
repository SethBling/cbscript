from cb_script.block_types.execute_base import execute_base


class while_block(execute_base):
    def __init__(self, line, exec_items, sub):
        self.line = line
        self.exec_items = exec_items
        self.sub = sub

    def compile(self, func):
        self.perform_execute(func)

    # Force a sub-function for the continuation commands
    def force_sub_function(self):
        return True

    # Adds the recursive continuation execute command to the end of the sub function
    def add_continuation_command(self, func, exec_func):
        dummy_func = exec_func.create_child_function()
        sub_cmd = "execute " + exec_func.get_execute_items(
            self.exec_items, dummy_func
        )

        if "$(" in sub_cmd:
            exec_func.has_macros = True

        if sub_cmd == None:
            raise Exception(
                f"Unable to compile continuation command for while block at line {self.line}"
            )

        exec_func.add_command(f"{sub_cmd}run {exec_func.get_call()}")

    def display_name(self):
        return "while"
