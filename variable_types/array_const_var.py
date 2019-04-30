from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var

class array_const_var(var_base):
	def __init__(self, array, idx):
		self.array = array
		self.idx = idx
		
	def get_objective(self, func):
		return func.get_arrayconst_var(self.array, self.idx.get_value(func))

	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		return scoreboard_var('Global', self.get_objective(func))
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return 'scoreboard players get Global {}'.format(self.get_objective(func))
		
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		return selector == 'Global' and objective == self.get_objective(func)
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		return self.get_objective(func)
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		const_val = var.get_const_value(func)
		if const_val:
			func.add_command('scoreboard players set Global {} {}'.format(self.get_objective(func), const_val))
		else:
			func.add_command('execute store result score Global {} run {}'.format(self.get_objective(func), var.get_command(func)))
			
	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var
