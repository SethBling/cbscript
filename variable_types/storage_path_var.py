from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var

class storage_path_var(var_base):
	def __init__(self, target, path_name):
		self.target = target
		self.path_name = path_name
		
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		if assignto == None:
			assignto = scoreboard_var('Global', func.get_scratch())
			
		func.add_command('execute store result score {} run {}'.format(assignto.get_selvar(func), self.get_command(func)))
			
		return assignto
		
	def get_target(self, func):
		if self.target == None:
			return func.namespace
		else:
			return self.target
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return 'data get storage {} {} 1'.format(self.get_target(func), self.path_name)
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		var_const = var.get_const_value(func)
		
		if var_const != None:
			func.add_command('data modify storage {} {} set value {}'.format(
				self.get_target(func),
				self.path_name,
				var_const
			))
		else:
			func.add_command('execute store result storage {} {} int 1 run {}'.format(
				self.get_target(func),
				self.path_name,
				var.get_command(func)
			))
		
		var.free_scratch(func)
		
	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var
