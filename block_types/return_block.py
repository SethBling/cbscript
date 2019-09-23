from block_base import block_base
from scoreboard_assignment_block import scoreboard_assignment_block
from variable_types.scoreboard_var import scoreboard_var

class return_block(block_base):
	def __init__(self, line, expr):
		self.expr = expr
		self.line = line
		
	def compile(self, func):
		return_var = scoreboard_var('Global', 'ReturnValue')
		assignment = scoreboard_assignment_block(self.line, return_var, '=', self.expr)
		assignment.compile(func)
		func.register_local('ReturnValue')