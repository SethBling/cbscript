from block_base import block_base
import traceback
from CompileError import CompileError

class import_block(block_base):
	def __init__(self, line, filename):
		self.line = line
		self.filename = filename
		
	def compile(self, func):
		try:
			func.import_file(self.filename + '.cblib')
		except SyntaxError as e:
			print(e)
			raise CompileError('Importing file "{}" failed at line {}:\n{}'.format(self.filename, self.line, e))
		except CompileError as e:
			print(e)
			raise CompileError('Importing file "{}" failed at line {}:\n{}'.format(self.filename, self.line, e))
		except Exception as e:
			print(traceback.format_exc())
			raise CompileError('Importing file "{}" failed at line {}:\n{}'.format(self.filename, self.line, e))