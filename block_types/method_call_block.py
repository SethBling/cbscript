from block_base import block_base

class method_call_block(block_base):
	def __init__(self, line, selector, dest, params, with_macros):
		self.line = line
		self.selector, self.dest, self.params, self.with_macros = selector, dest, params, with_macros
		
	def compile(self, func):
		if not func.evaluate_params(self.params):
			raise Exception('Unable to evaluate method call parameters at line {}'.format(self.line))
		
		cmd = ""

		if self.selector == '@s' or self.selector == '@s[]':
			# TODO: Make this handle macro arguments
			cmd = 'function {0}:{1}'.format(func.namespace, self.dest)
		else:
			cmd = 'execute as {0} run function {1}:{2}'.format(self.selector, func.namespace, self.dest)

		if self.with_macros:
			cmd += ' with storage {}:global args'.format(func.namespace)

		func.add_command(cmd)