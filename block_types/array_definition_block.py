from command_block import command_block
from variable_types.scoreboard_var import scoreboard_var

class array_definition_block(object):
	def __init__(self, line, name, from_val, to_val):
		self.line = line
		self.name = name
		self.from_val = from_val
		self.to_val = to_val
		
	def compile(self, func):
		try:
			from_val = int(self.from_val.get_value(func))
			to_val = int(self.to_val.get_value(func))
		except Exception:
			raise Exception('Unable to get array range for "{}" at line {}'.format(self.name, self.line))
			
		name = self.name

		vals = list(range(from_val, to_val))
		
		for i in vals:
			func.register_objective('{}{}'.format(name, i))
		
		valvar = '{}Val'.format(name)
		func.register_objective(valvar)
		
		indexvar = scoreboard_var('Global', '{}Idx'.format(name))
		
		get_func = func.create_child_function()
		get_func_name = 'array_{}_get'.format(name.lower())
		func.register_function(get_func_name, get_func)
		cases = [(i, i, [command_block(self.line, '/scoreboard players operation Global {} = Global {}{}'.format(valvar, name, i))], self.line, None) for i in vals]
		if not get_func.switch_cases(indexvar, cases, 'arrayget', 'arraygetidx'):
			raise Exception('Error creating getter for array at line {}'.format(self.line))
		
		set_func = func.create_child_function()
		set_func_name = 'array_{}_set'.format(name.lower())
		func.register_function(set_func_name, set_func)
		cases = [(i, i, [command_block(self.line, '/scoreboard players operation Global {}{} = Global {}'.format(name, i, valvar))], self.line, None) for i in vals]
		if not set_func.switch_cases(indexvar, cases, 'arrayset', 'arraysetidx'):
			raise Exception('Error creating setter for array at line {}'.format(self.line))
			
		func.register_array(name, from_val, to_val)