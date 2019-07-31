from block_base import block_base

class method_call_block(block_base):
	def __init__(self, line, selector, dest, params):
		self.line = line
		self.selector, self.dest, self.params = selector, dest, params
		
	def compile(self, func):
		if not func.evaluate_params(self.params):
			raise Exception('Unable to evaluate method call parameters at line {}'.format(self.line))
		
		if self.selector == '@s' or self.selector == '@s[]':
			func.add_command('function {0}:{1}'.format(func.namespace, self.dest))
		else:
			func.add_command('execute as {0} run function {1}:{2}'.format(self.selector, func.namespace, self.dest))