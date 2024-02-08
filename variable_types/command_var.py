from var_base import var_base
from scoreboard_var import scoreboard_var
from CompileError import CompileError

class command_var(var_base):
	def __init__(self, output, command):
		self.output = output
		if command.startswith('/'):
			command = command[1:]
		self.command = command

	# Returns a scoreboard objective for this variable.
	# If assignto isn't None, then this function may
	# use the assignto objective to opimtize data flow.
	def get_scoreboard_var(self, func, assignto=None):
		if assignto == None:
			assignto = scoreboard_var('Global', func.get_scratch())
			
		func.add_command('execute store {} score {} run {}'.format(self.output, assignto.get_selvar(func), self.command))
			
		return assignto
	
	# Returns a command that will get this variable's value to be used with "execute store result"
	def get_command(self, func):
		return self.command
	
	# Copies the value from a target variable to this variable
	def copy_from(self, func, var):
		raise CompileError('Cannot set the value of a command.')

	# Returns a scoreboard_var which can be modified as needed without side effects
	def get_modifiable_var(self, func, assignto):
		return self.get_scoreboard_var(func, assignto)