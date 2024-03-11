from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var

class array_expr_var(var_base):
	def __init__(self, selector, array, idx_expr):
		self.selector = selector
		self.array = array
		self.idx_expr = idx_expr
		
	def check_defined(self, func):
		if self.array not in func.arrays:
			print(f'Tried to use undefined array "{self.array}"')
			return None
			
		from_val, to_val, selector_based = func.arrays[self.array]
		
		if selector_based and self.selector == 'Global':
			raise CompileError(f'Tried to use selector-based array {self.array} without a selector.')
		if not selector_based and self.selector != 'Global':
			raise CompileError(f'Tried to use global array {self.array} with a selector.')

	def evaluate(self, func):
		self.check_defined(func)
	
		index_name = f'{self.array}Idx'
		expr_var = self.idx_expr.compile(func, index_name)
		
		index_var = scoreboard_var(self.selector, index_name)
		index_var.copy_from(func, expr_var)
		
		if self.selector == '@s' or not self.selector.startswith('@'):
			prefix = ''
		else:
			prefix = f'execute as {self.selector} run '
		
		func.add_command(prefix + f'function {func.namespace}:array_{self.array.lower()}_get')

		expr_var.free_scratch(func)
		
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		self.evaluate(func)
		
		return scoreboard_var(self.selector, f'{self.array}Val')
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return self.get_scoreboard_var(func).get_command(func)
	
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		self.check_defined(func)
		
		return selector == self.selector and objective == f'{self.array}Idx'
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		self.check_defined(func)
		
		return scoreboard_var(f'Global', '{self.array}Idx')
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		self.check_defined(func)
	
		index_name = f'{self.array}Idx'
		index_var = scoreboard_var(self.selector, index_name)
		
		expr_var = self.idx_expr.compile(func, index_name)
		index_var.copy_from(func, expr_var)
		
		val_name = f'{self.array}Val'
		val_var = scoreboard_var(self.selector, val_name)
		
		val_var.copy_from(func, var)
		
		if self.selector == '@s' or not self.selector.startswith('@'):
			prefix = ''
		else:
			prefix = f'execute as {self.selector} run '
		
		func.add_command(prefix + f'function {func.namespace}:array_{self.array.lower()}_set')
		
		expr_var.free_scratch(func)
		val_var.free_scratch(func)


	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var
	
	# Returns true if this varariable/expression references the specified scoreboard variable
	def references_scoreboard_var(self, func, var):
		return self.idx_expr.references_scoreboard_var(func, var)