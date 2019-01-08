class function_call_block(block_type):
	def __init__(self, line, dest, params):
		self.line = line
		self.dest = dest
		self.params = params
		
	def compile(self, func):
		if not evaluate_params(func, self.params):
			raise Exception('Unable to evaluate function call parameters at line {}'.format(self.line))
		
		func.add_command('function {0}:{1}'.format(func.namespace, self.dest))