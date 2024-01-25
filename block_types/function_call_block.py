from block_base import block_base

class function_call_block(block_base):
	def __init__(self, line, dest, args, with_macros):
		self.line = line
		self.dest, self.args, self.with_macros = dest, args, with_macros
		
	def compile(self, func):
		if self.dest == func.name:
			locals = func.get_local_variables()
			func.push_locals(locals)
			
		if not func.evaluate_params(self.args):
			raise Exception('Unable to evaluate function call parameters at line {}'.format(self.line))
		
		cmd = ""

		if ':' in self.dest:
			cmd = 'function {}'.format(self.dest)
		else:
			# Default to this datapack's namespace
			# TODO: Make this handle macro arguments
			cmd = 'function {}:{}'.format(func.namespace, self.dest)

		if self.with_macros:
			cmd += ' with storage {}:global args'.format(func.namespace)

		func.add_command(cmd)

		if self.dest == func.name:
			func.pop_locals(locals)