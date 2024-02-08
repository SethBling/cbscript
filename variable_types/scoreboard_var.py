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
			
	# Returns a scoreboard_var for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		path_data = self.get_path(func)
		
		if path_data:
			if assignto == None:
				assignto = scoreboard_var('Global', func.get_scratch())
			
			assignto.copy_from(func, self)
				
			return assignto
		else:
			func.register_objective(self.objective)

			name_def = func.get_name_definition(self.selector)
			if name_def != None:
				return scoreboard_var(name_def, self.objective)
			
			return self
		
	def compile(self, func, assignto=None):
		name_def = func.get_name_definition(self.selector)
		if name_def != None:
			return scoreboard_var(name_def, self.objective)
		else:
			return self
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		path_data = self.get_path(func)
		if path_data:
			path, data_type, scale = path_data
			return 'data get entity {} {} {}'.format(self.selector, path, scale)
		else:		
			func.register_objective(self.objective)

			selector = self.selector
			name_def = func.get_name_definition(self.selector)
			if name_def != None:
				selector = name_def
			
			return 'scoreboard players get {} {}'.format(selector, self.objective)
	
	# Returns an execute prefix that can be used to set this variable's value when paired with a get_command() command
	def set_command(self, func):
		path_data = self.get_path(func)
		if path_data:
			path, data_type, scale = path_data
			return 'execute store result entity {} {} {} {}'.format(self.selector, path, data_type, 1/float(scale))
		else:		
			func.register_objective(self.objective)

			selector = self.selector
			name_def = func.get_name_definition(self.selector)
			if name_def != None:
				selector = name_def
		
			return 'execute store result score {} {}'.format(selector, self.objective)
			
	# Gets a constant integer value for this variable if there is one, otherwise returns None.
	def get_const_value(self, func):
		return None
		
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		path_data = self.get_path(func)
		
		myselector = self.selector
		name_def = func.get_name_definition(self.selector)
		if name_def != None:
			myselector = name_def

		if path_data == None and myselector == selector and self.objective == objective:
			return True
		else:
			return False
		
	def same_as(self, func, var):
		if var == None:
			return False

		myselector = self.selector
		name_def = func.get_name_definition(self.selector)
		if name_def != None:
			myselector = name_def

		return var.is_objective(func, myselector, self.objective)
	
	def is_fast_selector(self):
		if not self.selector.startswith('@'):
			return True
		
		if self.selector == '@s':
			return True
		
		return False
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		path_data = self.get_path(func)
		if path_data == None and self.is_fast_selector():
			func.register_objective(self.objective)
			
			return self
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

			selector = self.selector
			name_def = func.get_name_definition(self.selector)
			if name_def != None:
				selector = name_def
			
			if var_const != None:
				func.add_command('scoreboard players set {} {} {}'.format(selector, self.objective, var_const))
			elif not var.is_objective(func, selector, self.objective):
				selvar = var.get_selvar(func)

				if selvar == None:
					func.add_command('{} run {}'.format(self.set_command(func), var.get_command(func)))
				else:
					func.add_command('scoreboard players operation {} {} = {}'.format(selector, self.objective, selvar))

	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		path_data = self.get_path(func)
		
		if path_data:
			return self.get_scoreboard_var(func, assignto)
		else:
			func.register_objective(self.objective)
			
			if self.selector == 'Global' and func.is_scratch(self.objective):
				return self
			elif self.same_as(func, assignto):
				return self
			else:
				modifiable_var = scoreboard_var('Global', func.get_scratch())
				modifiable_var.copy_from(func, self)
				
				return modifiable_var
				
	# If this is a scratch variable, free it up
	def free_scratch(self, func):
		func.free_scratch(self.objective)

	def uses_macro(self, func):
		return func.get_name_definition(self.selector) != None or "$(" in self.selector
		
	# Returns the selector and objective of this variable if it is a scoreboard_var, otherwise returns None
	def get_selvar(self, func):
		path_data = self.get_path(func)
		if path_data:
			return None

		name_def = func.get_name_definition(self.selector)
		
		if name_def != None:
			return '{} {}'.format(name_def, self.objective)
		else:
			return '{} {}'.format(self.selector, self.objective)

	# This should only be used for scoreboard variables that are known to
	# be Global
	@property
	def selvar(self):
		return '{} {}'.format(self.selector, self.objective)