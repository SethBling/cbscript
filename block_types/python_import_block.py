from .block_base import block_base
import traceback
from CompileError import CompileError, Pos

class python_import_block(block_base):
	def __init__(self, line, filename):
		self.line = line
		self.filename = filename
		
	def compile(self, func):
		try:
			func.import_python_file(self.filename + '.py')
		except SyntaxError as e:
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}', Pos(self.line)) from e
		except CompileError as e:
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}', Pos(self.line)) from e
		except Exception as e:
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}', Pos(self.line)) from e
