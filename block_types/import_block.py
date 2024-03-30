from .block_base import block_base
import traceback
from CompileError import CompileError, Pos

class import_block(block_base):
	def __init__(self, line, filename):
		self.line = line
		self.filename = filename
		
	def compile(self, func):
		try:
			func.import_file(self.filename + '.cblib')
		except SyntaxError as e:
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}:\n{e}',Pos(self.line)) from e
		except CompileError as e:
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}:\n{e}',Pos(self.line)) from e
		except FileNotFoundError:
			raise CompileError(f'Could not find file "{self.filename}", at line {self.line}',Pos(self.line)) from None
		except Exception as e:
			print(traceback.format_exc())
			raise CompileError(f'Importing file "{self.filename}" failed at line {self.line}:\n{e}',Pos(self.line)) from e
