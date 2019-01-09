from cbscript import compile_block

class macro_call_block(object):
	def __init__(self, line, macro, args):
		self.line = line
		self.macro = macro
		self.args = args
		
	def compile(self, func):
		if self.macro not in func.macros:
			raise ValueError('Line {1}: macro "{0}" does not exist'.format(self.macro, get_line(line)))
			
		params, sub = func.macros[self.macro]
			
		if len(self.args) != len(params):
			print('Tried to call Macro "{0}" with {1} arguments at line {3}, but it requires {2}'.format(macro, len(args), len(params), get_line(line)))
			return False
			
		new_env = func.clone_environment()
			
		for p in range(len(params)):
			if isNumber(self.args[p]):
				if self.args[p].isdigit() or self.args[p][0] == '-' and self.args[p][1:].isdigit():
					new_env.set_dollarid(params[p], int(self.args[p]))
				else:
					new_env.set_dollarid(params[p], float(self.args[p]))
			elif self.args[p].startswith('$'):
				new_env.copy_dollarid(params[p], self.args[p])
			else:
				print('Unknown macro parameter "{}" in macro call at line {}'.format(self.args[p], self.line))
				
		func.push_environment(new_env)
		if not compile_block(func, sub):
			raise Exception('Unable to compile macro call at line {}'.format(self.line))
		func.pop_environment()