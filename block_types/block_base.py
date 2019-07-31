from CompileError import CompileError
import traceback

class block_base(object):
	def compile(self, func):
		raise NotImplementedError('Section does not implement compile()')
		
	def register(self, global_context):
		None
		
	def compile_lines(self, func, lines):
		try:
			func.compile_blocks(lines)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile {} at line {}'.format(self.name, self.line))
		except e:
			print(traceback.format_exc())
			raise CompileError('Error compiling {} at line {}'.format(self.name, self.line))
		
	@property
	def block_name(self):
		return 'block'