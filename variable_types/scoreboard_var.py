from variable_types.var_base import var_base

class scoreboard_var(var_base):
	def __init__(self, selector, objective):
		self.selector = selector
		self.objective = objective
		
	def get_path(self, func):
		if self.selector.startswith('@s'):
			seldef = func.get_self_selector_definition()
		else:
			seldef = func.get_selector_definition(self.selector)
			
		if seldef != None:
			if self.objective in seldef.paths:
				return seldef.paths[self.objective]			
				
		return None
			
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		path_data = self.get_path(func)
		
		if path_data:
			if assignto == None:
				assignto = func.get_scratch()
				
			ret = scoreboard_var('Global', assignto)
			ret.copy_from(func, self)
				
			return scoreboard_var('Global', assignto)
		else:
			func.register_objective(self.objective)
			
			return self
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		path_data = self.get_path(func)
		if path_data:
			path, data_type, scale = path_data
			return 'data get entity {} {} {}'.format(self.selector, path, scale)
		else:		
			func.register_objective(self.objective)
			
			return 'scoreboard players get {} {}'.format(self.selector, self.objective)
	
	# Returns an execute prefix that can be used to set this variable's value when paired with a get_command() command
	def set_command(self, func):
		path_data = self.get_path(func)
		if path_data:
			path, data_type, scale = path_data
			return 'execute store result entity {} {} {} {}'.format(self.selector, path, data_type, 1/float(scale))
		else:		
			func.register_objective(self.objective)
		
			return 'execute store result score {} {}'.format(self.selector, self.objective)
			
	# Gets a constant integer value for this variable if there is one, otherwise returns None.
	def get_const_value(self, func):
		return None
		
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		path_data = self.get_path(func)
		if path_data == None and self.selector == selector and self.objective == objective:
			return True
		else:
			return False
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		path_data = self.get_path(func)
		if path_data == None and self.selector == 'Global':
			func.register_objective(self.objective)
			
			return self.objective
		else:
			return None
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		path_data = self.get_path(func)
		
		var_const = var.get_const_value(func)
		
		if path_data:
			path, data_type, scale = path_data
			
			if var_const != None:
				suffix = {
					'byte': 'b',
					'short': 's',
					'int': '',
					'long': 'L',
					'float': 'f',
					'double': 'd',
				}
				if data_type != 'float' and data_type != 'double':
					val = int(var_const / scale)
				else:
					val = float(var_const) / float(scale)
					
				func.add_command('data modify entity {} {} set value {}{}'.format(self.selector, path, val, suffix[data_type]))
			else:
				func.add_command('{} run {}'.format(self.set_command(func), var.get_command(func)))
		else:
			func.register_objective(self.objective)
			
			if var_const != None:
				func.add_command('scoreboard players set {} {} {}'.format(self.selector, self.objective, var_const))
			elif not var.is_objective(func, self.selector, self.objective):
				func.add_command('{} run {}'.format(self.set_command(func), var.get_command(func)))

	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		path_data = self.get_path(func)
		
		if path_data:
			return self.get_scoreboard_var(func, assignto)
		else:
			func.register_objective(self.objective)
			
			if self.selector == 'Global' and func.is_scratch(self.objective):
				return self
			elif self.selector == 'Global' and self.objective == assignto:
				return self
			else:
				modifiable_var = scoreboard_var('Global', func.get_scratch())
				modifiable_var.copy_from(func, self)
				func.is_scratch(self.objective)
				return modifiable_var
				
	# If this is a scratch variable, free it up
	def free_scratch(self, func):
		func.free_scratch(self.objective)
		
	@property
	def selvar(self):
		return '{} {}'.format(self.selector, self.objective)