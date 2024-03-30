from .block_base import block_base
from .command_block import command_block
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError, Pos

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
			raise CompileError(f'Unable to get array range for "{self.name}" at line {self.line}', Pos(self.line)) from None
			
		name = self.name

		vals = list(range(from_val, to_val))
		
		for i in vals:
			func.register_objective(f'{name}{i}')
		
		valvar = f'{name}Val'
		func.register_objective(valvar)
		
		selector = '@s' if self.selector_based else 'Global'
		
		indexvar = scoreboard_var(selector, f'{name}Idx')
		
		get_func = func.create_child_function()
		get_func_name = f'array_{name.lower()}_get'
		func.register_function(get_func_name, get_func)
		cases = [(i, i, [command_block(self.line, f'/scoreboard players operation {selector} {valvar} = {selector} {name}{i}')], self.line, None) for i in vals]
		if not get_func.switch_cases(indexvar, cases, 'arrayget', 'arraygetidx'):
			raise Exception(f'Error creating getter for array at line {self.line}')
		
		set_func = func.create_child_function()
		set_func_name = f'array_{name.lower()}_set'
		func.register_function(set_func_name, set_func)
		cases = [(i, i, [command_block(self.line, f'/scoreboard players operation {selector} {name}{i} = {selector} {valvar}')], self.line, None) for i in vals]
		if not set_func.switch_cases(indexvar, cases, 'arrayset', 'arraysetidx'):
			raise Exception(f'Error creating setter for array at line {self.line}')
			
		func.register_array(name, from_val, to_val, self.selector_based)
