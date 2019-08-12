from block_base import block_base

class function_section(block_base):
	def __init__(self, line, name, params, lines):
		self.line = line
		self.name = name
		self.params = params
		self.lines = lines
		self.self_selector = None
		
	def compile(self, func):
		func_func = func.create_child_function(
			new_function_name = self.name,
			callable = True,
			params = self.params
		)
		func.register_function(self.name, func_func)
		
		if self.self_selector:
			func_func.update_self_selector(self.self_selector)
		self.compile_lines(func_func, self.lines)
		
	def register(self, global_context):
		global_context.register_function_params(self.name, self.params)
		
	@property
	def block_name(self):
		return 'function "{}"'.format(self.name)
