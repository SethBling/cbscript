from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError

class array_const_var(var_base):
	def __init__(self, selector, array, idx):
		self.selector = selector
		self.array = array
		self.idx = idx
		
	def check_array(self, func):
		try:
			idx_str = func.apply_replacements(self.idx)
			val = int(idx_str)
		except Exception as e:
			print(e)
			raise CompileError('"{}" is not an integer for array "{}" index'.format(idx_str, self.array))
			
		if self.array not in func.arrays:
			raise CompileError('Tried to use undefined array {}'.format(self.array))
		from_val, to_val, selector_based = func.arrays[self.array]
		if val < from_val or val > to_val:
			raise CompileError('Index {} for "array {}[{} to {}]" is out of bounds.'.format(val, self.array, from_val, to_val))

		if selector_based and self.selector == 'Global':
			raise CompileError('Tried to use selector-based array {} without a selector.'.format(self.array))
		if not selector_based and self.selector != 'Global':
			raise CompileError('Tried to use global array {} with a selector.'.format(self.array))
	
	def get_objective(self, func):
		self.check_array(func)
		idx_str = func.apply_replacements(self.idx)
		return '{}{}'.format(self.array, idx_str)

	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		return scoreboard_var(self.selector, self.get_objective(func))
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return 'scoreboard players get {} {}'.format(self.selector, self.get_objective(func))
		
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		return selector == self.selector and objective == self.get_objective(func)
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		return scoreboard_var('Global', self.get_objective(func))
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		const_val = var.get_const_value(func)
		if const_val != None:
			func.add_command('scoreboard players set {} {} {}'.format(self.selector, self.get_objective(func), const_val))
		else:
			func.add_command('execute store result score {} {} run {}'.format(self.selector, self.get_objective(func), var.get_command(func)))
			
	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var

	# Returns true if this varariable/expression references the specified scoreboard variable
	def references_scoreboard_var(self, func, var):
		return self.get_scoreboard_var(func).references_scoreboard_var(func, var)
