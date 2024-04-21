import traceback

from cb_script.block_types.block_base import block_base
from cb_script.CompileError import CompileError


class python_import_block(block_base):
    def __init__(self, line, filename):
        self.line = line
        self.filename = filename

    def compile(self, func):
        try:
            func.import_python_file(self.filename + ".py")
        except SyntaxError as e:
            print(e)
            raise CompileError(
                f'Importing file "{self.filename}" failed at line {self.line}:\n{e}'
            )
        except CompileError as e:
            print(e)
            raise CompileError(
                f'Importing file "{self.filename}" failed at line {self.line}:\n{e}'
            )
        except Exception as e:
            print(traceback.format_exc())
            raise CompileError(
                f'Importing file "{self.filename}" failed at line {self.line}:\n{e}'
            )
