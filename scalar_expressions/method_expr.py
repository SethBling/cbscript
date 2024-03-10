from .scalar_expression_base import scalar_expression_base
from variable_types.scoreboard_var import scoreboard_var
from environment import isInt
import math

class method_expr(scalar_expression_base):
	def __init__(self, method_call):
		self.method_call = method_call
	
	def compile(self, func, assignto=None):
		self.method_call.compile(func)
		
		return scoreboard_var('Global', 'ReturnValue')