from CompileError import CompileError, Pos
import traceback

class block_base(object):
	def __init__(self, line):
		self.line = line
	def compile(self, func):
		raise NotImplementedError('Section does not implement compile()')
		
	def register(self, global_context):
		None
		
	def compile_lines(self, func, lines):
		try:
			func.compile_blocks(lines)
		except CompileError as e:
			raise CompileError(f'Unable to compile {self.block_name} at line {self.line}', Pos(self.line)) from e
		except Exception as e:
			raise CompileError(f'Error compiling {self.block_name} at line {self.line}', Pos(self.line)) from e
		
	@property
	def block_name(self):
		return 'block'
