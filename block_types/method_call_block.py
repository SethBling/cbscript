from .call_block_base import call_block_base

class method_call_block(call_block_base):
	def __init__(self, line, selector, dest, params, with_macro_items):
		self.line = line
		self.selector, self.dest, self.params, self.with_macro_items = selector, dest, params, with_macro_items
		
	def compile(self, func):
		self.compile_with_macro_items(func)
		
		if not func.evaluate_params(self.params):
			raise Exception(f'Unable to evaluate method call parameters at line {self.line}')
		
		cmd = ""

		if self.selector == '@s' or self.selector == '@s[]':
			cmd = f'function {func.namespace}:{self.dest}'
		else:
			cmd = f'execute as {self.selector} run function {func.namespace}:{self.dest}'

		if self.with_macro_items != None:
			cmd += f' with storage {func.namespace}:global args'
			self.has_macros = True

		func.add_command(cmd)
