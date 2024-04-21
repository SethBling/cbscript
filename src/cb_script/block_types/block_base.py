import traceback

from cb_script.CompileError import CompileError


class block_base(object):
    def compile(self, func):
        raise NotImplementedError("Section does not implement compile()")

    def register(self, global_context):
        None

    def compile_lines(self, func, lines):
        try:
            func.compile_blocks(lines)
        except CompileError as e:
            print(e)
            raise CompileError(
                f"Unable to compile {self.block_name} at line {self.line}"
            )
        except e:
            print(traceback.format_exc())
            raise CompileError(
                f"Error compiling {self.block_name} at line {self.line}"
            )

    @property
    def block_name(self):
        return "block"
