from block_base import block_base

class function_call_block(block_base):
	def __init__(self, line, dest, args):
		self.line = line
		self.dest, self.args = dest, args
		
	def compile(self, func):
		if self.dest == func.name:
			locals = func.get_local_variables()
			func.push_locals(locals)
			
		if not func.evaluate_params(self.args):
			raise Exception('Unable to evaluate function call parameters at line {}'.format(self.line))
		
		if ':' in self.dest:
			func.add_command('function {}'.format(self.dest))
		else:
			# Default to this datapack's namespace
			func.add_command('function {}:{}'.format(func.namespace, self.dest))

		if self.dest == func.name:
			func.pop_locals(locals)