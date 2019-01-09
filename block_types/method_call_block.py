class method_call_block(object):
	def __init__(self, line, selector, dest, params):
		self.line = line
		self.selector = selector
		self.dest = dest
		self.params = params
		
	def compile(self, func):
		if not evaluate_params(func, self.params):
			raise Exception('Unable to evaluate method call parameters at line {}'.format(self.line))
		
		if selector == '@s':
			func.add_command('function {0}:{1}'.format(func.namespace, self.dest))
		else:
			func.add_command('execute as {0} run function {1}:{2}'.format(self.selector, func.namespace, self.dest))