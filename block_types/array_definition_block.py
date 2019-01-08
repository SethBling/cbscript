from cbscript import switch_cases

class array_definition_block(block_type):
	def __init__(self, line, name, from_val, to_val):
		self.line = line
		self.name = name
		self.from_val = from_val
		self.to_val = to_val
		
	def compile(self, func):
		from_val = int(func.apply_replacements(self.from_val))
		to_val = int(func.apply_replacements(self.to_val))
		name = self.name

		vals = list(range(from_val, to_val))
		
		for i in vals:
			func.register_objective('{}{}'.format(name, i))
		
		valvar = '{}Val'.format(name)
		func.register_objective(valvar)
		
		indexvar = '{}Idx'.format(name)
		func.register_objective(indexvar)
		
		get_func = mcfunction(func.clone_environment())
		get_func_name = 'array_{}_get'.format(name.lower())
		func.register_function(get_func_name, get_func)
		cases = [(i, i, [('Command', '/scoreboard players operation Global {} = Global {}{}'.format(valvar, name, i))], self.line, None) for i in vals]
		if not switch_cases(get_func, indexvar, cases, 'arrayget', 'arraygetidx'):
			raise Exception('Error creating getter for array at line {}'.format(self.line))
		
		set_func = mcfunction(func.clone_environment())
		set_func_name = 'array_{}_set'.format(name.lower())
		func.register_function(set_func_name, set_func)
		cases = [(i, i, [('Command', '/scoreboard players operation Global {}{} = Global {}'.format(name, i, valvar))], self.line, None) for i in vals]
		if not switch_cases(set_func, indexvar, cases, 'arrayset', 'arraysetidx'):
			raise Exception('Error creating setter for array at line {}'.format(self.line))
			
		func.register_array(name, from_val, to_val)