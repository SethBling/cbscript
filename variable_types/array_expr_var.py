from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var

class array_expr_var(var_base):
	def __init__(self, selector, array, idx_expr):
		self.selector = selector
		self.array = array
		self.idx_expr = idx_expr
		
	def check_defined(self, func):
		if self.array not in func.arrays:
			print('Tried to use undefined array "{}"'.format(self.array))
			return None
			
		from_val, to_val, selector_based = func.arrays[self.array]
		
		if selector_based and self.selector == 'Global':
			raise CompileError('Tried to use selector-based array {} without a selector.'.format(self.array))
		if not selector_based and self.selector != 'Global':
			raise CompileError('Tried to use global array {} with a selector.'.format(self.array))

	def evaluate(self, func):
		self.check_defined(func)
	
		index_name = '{}Idx'.format(self.array)
		expr_var = self.idx_expr.compile(func, index_name)
		
		index_var = scoreboard_var(self.selector, index_name)
		index_var.copy_from(func, expr_var)
		
		if self.selector == '@s':
			prefix = ''
		else:
			prefix = 'execute as {} run '.format(self.selector)
		
		func.add_command(prefix + 'function {}:array_{}_get'.format(func.namespace, self.array.lower()))

		expr_var.free_scratch(func)
		
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		self.evaluate(func)
		
		return scoreboard_var(self.selector, '{}Val'.format(self.array))
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return self.get_scoreboard_var(func).get_command(func)
	
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		self.check_defined(func)
		
		return selector == self.selector and objective == '{}Idx'.format(self.array)
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		self.check_defined(func)
		
		return '{}Idx'.format(self.array)
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		self.check_defined(func)
	
		index_name = '{}Idx'.format(self.array)
		index_var = scoreboard_var(self.selector, index_name)
		
		expr_var = self.idx_expr.compile(func, index_name)
		index_var.copy_from(func, expr_var)
		
		val_name = '{}Val'.format(self.array)
		val_var = scoreboard_var(self.selector, val_name)
		
		val_var.copy_from(func, var)
		
		if self.selector == '@s':
			prefix = ''
		else:
			prefix = 'execute as {} run '.format(self.selector)
		
		func.add_command(prefix + 'function {}:array_{}_set'.format(func.namespace, self.array.lower()))
		
		expr_var.free_scratch(func)
		val_var.free_scratch(func)


	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var