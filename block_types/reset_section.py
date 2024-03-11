from .block_base import block_base

class reset_section(block_base):
	def __init__(self, line, lines):
		self.line = line
		self.lines = lines
		
	def compile(self, func):
		reset_func = func.get_reset_function()
		if reset_func == None:
			reset_func = func.create_child_function()
			func.register_function('reset', reset_func)
			
		reset_func.copy_environment_from(func)
		
		self.compile_lines(reset_func, self.lines)
		
	@property
	def block_name(self):
		return 'reset section'