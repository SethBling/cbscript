from call_block_base import call_block_base

class method_call_block(call_block_base):
	def __init__(self, line, selector, dest, params, with_macro_items):
		self.line = line
		self.selector, self.dest, self.params, self.with_macro_items = selector, dest, params, with_macro_items
		
	def compile(self, func):
		self.compile_with_macro_items(func)
		
		if not func.evaluate_params(self.params):
			raise Exception('Unable to evaluate method call parameters at line {}'.format(self.line))
		
		cmd = ""

		if self.selector == '@s' or self.selector == '@s[]':
			cmd = 'function {0}:{1}'.format(func.namespace, self.dest)
		else:
			cmd = 'execute as {0} run function {1}:{2}'.format(self.selector, func.namespace, self.dest)

		if self.with_macro_items != None:
			cmd += ' with storage {}:global args'.format(func.namespace)

		func.add_command(cmd)