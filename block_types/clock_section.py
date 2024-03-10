from .block_base import block_base

class clock_section(block_base):
	def __init__(self, line, id, lines):
		self.line = line
		self.id = id
		self.lines = lines
		
	def compile(self, func):
		clock_func = func.create_child_function(new_function_name = self.id)
		func.register_clock(self.id)
		func.register_function(self.id, clock_func)
		self.compile_lines(clock_func, self.lines)
		
	@property
	def block_name(self):
		return 'clock "{}"'.format(self.id)