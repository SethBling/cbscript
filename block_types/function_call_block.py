from block_types.call_block_base import call_block_base

class function_call_block(call_block_base):
	def __init__(self, line, dest, args, with_macro_items):
		self.line = line
		self.dest, self.args, self.with_macro_items = dest, args, with_macro_items
		
	def compile(self, func):
		if self.dest == func.name:
			locals = func.get_local_variables()
			func.push_locals(locals)

		self.compile_with_macro_items(func)
			
		if not func.evaluate_params(self.args):
			raise Exception('Unable to evaluate function call parameters at line {}'.format(self.line))
		
		cmd = ""

		if ':' in self.dest:
			cmd = 'function {}'.format(self.dest)
		else:
			# Default to this datapack's namespace
			cmd = 'function {}:{}'.format(func.namespace, self.dest)

		if self.with_macro_items != None:
			cmd += ' with storage {}:global args'.format(func.namespace)
			func.has_macros = True

		func.add_command(cmd)

		if self.dest == func.name:
			func.pop_locals(locals)
