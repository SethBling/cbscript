class function_call_block(object):
	def __init__(self, line, dest, args):
		self.line = line
		self.dest, self.args = dest, args
		
	def compile(self, func):
		if not func.evaluate_params(self.args):
			raise Exception('Unable to evaluate function call parameters at line {}'.format(self.line))
		
		func.add_command('function {0}:{1}'.format(func.namespace, self.dest))