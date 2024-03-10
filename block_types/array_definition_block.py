from .block_base import block_base
from .command_block import command_block
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError

class array_definition_block(block_base):
	def __init__(self, line, name, from_val, to_val, selector_based):
		self.line = line
		self.name = name
		self.from_val = from_val
		self.to_val = to_val
		self.selector_based = selector_based
		
	def compile(self, func):
		try:
			from_val = int(self.from_val.get_value(func))
			to_val = int(self.to_val.get_value(func))
		except Exception:
			raise CompileError('Unable to get array range for "{}" at line {}'.format(self.name, self.line))
			
		name = self.name

		vals = list(range(from_val, to_val))
		
		for i in vals:
			func.register_objective('{}{}'.format(name, i))
		
		valvar = '{}Val'.format(name)
		func.register_objective(valvar)
		
		selector = '@s' if self.selector_based else 'Global'
		
		indexvar = scoreboard_var(selector, '{}Idx'.format(name))
		
		get_func = func.create_child_function()
		get_func_name = 'array_{}_get'.format(name.lower())
		func.register_function(get_func_name, get_func)
		cases = [(i, i, [command_block(self.line, '/scoreboard players operation {0} {1} = {0} {2}{3}'.format(selector, valvar, name, i))], self.line, None) for i in vals]
		if not get_func.switch_cases(indexvar, cases, 'arrayget', 'arraygetidx'):
			raise Exception('Error creating getter for array at line {}'.format(self.line))
		
		set_func = func.create_child_function()
		set_func_name = 'array_{}_set'.format(name.lower())
		func.register_function(set_func_name, set_func)
		cases = [(i, i, [command_block(self.line, '/scoreboard players operation {0} {1}{2} = {0} {3}'.format(selector, name, i, valvar))], self.line, None) for i in vals]
		if not set_func.switch_cases(indexvar, cases, 'arrayset', 'arraysetidx'):
			raise Exception('Error creating setter for array at line {}'.format(self.line))
			
		func.register_array(name, from_val, to_val, self.selector_based)