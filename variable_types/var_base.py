# Base class for Minecraft variables. Each variable subclass must implement at least one of the get() functions.
# If the variable is settable, it must implement set_value as well.
class var_base(object):
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		raise NotImplementedError()
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		raise NotImplementedError()
	
	# Gets a constant integer value for this variable if there is one, otherwise returns None.
	def get_const_value(self, func):
		return None
		
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		return False
			
	# Gets an assignto value for this variable if there is one.
	def get_assignto(self, func):
		return None
		
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		raise NotImplementedError()

	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		raise NotImplementedError()
		
	# If this is a scratch variable, free it up
	def free_scratch(self, func):
		None

	def get_global_id(self):
		return None
	
	# Returns the selector and objective of this variable if it is a scoreboard_var, otherwise returns None
	def get_selvar(self, func):
		return None
		
	# Used to evaluate a variable as an expression
	def compile(self, func, assignto=None):
		return self