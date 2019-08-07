from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError

class virtualint_var(var_base):
	def __init__(self, val):
		self.val = val
		
	def get_value(self, func):
		return int(func.apply_replacements(self.val))
	
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		return scoreboard_var(func.add_constant(self.get_value(func)), 'Constant')
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return 'scoreboard players get {} Constant'.format(func.add_constant(self.get_value(func)))
	
	# Gets a constant integer value for this variable if there is one, otherwise returns None.
	def get_const_value(self, func):
		return self.get_value(func)
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		raise CompileError('Cannot set the value of a constant.')
		
	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var
