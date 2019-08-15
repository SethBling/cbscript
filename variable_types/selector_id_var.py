from variable_types.var_base import var_base
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError

class selector_id_var(var_base):
	def __init__(self, selector):
		self.selector = selector

	def initialize_id(self, func):
		if not func.check_single_entity(self.selector):
			raise CompileError('Selector "{}" does not specify an individual entity.'.format(self.selector))
	
		func.register_objective('_unique')
		func.register_objective('_id')
		func.add_command('scoreboard players add Global _unique 1')
		func.add_command('execute unless score {0} _id matches 1.. run scoreboard players operation {0} _id = Global _unique'.format(self.selector))
		
	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		self.initialize_id(func)
		return scoreboard_var(self.selector, '_id')
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		self.initialize_id(func)
		return scoreboard_var(self.selector, '_id',).get_command(func)
	
	# Returns true if this variable is a scoreboard_var with the specified selector and objective,
	# to reduce extranious copies.
	def is_objective(self, func, selector, objective):
		return selector == self.selector and objective == '_id'
			
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		id_scoreboard_var = scoreboard_var(self.selector, '_id')
		id_scoreboard_var.copy_from(var)
		
		var.free_scratch(func)
		
	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		scratch_var = scoreboard_var('Global', func.get_scratch())
		scratch_var.copy_from(func, self)
		return scratch_var
