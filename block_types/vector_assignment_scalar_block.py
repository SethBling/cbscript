from vector_assignment_base import vector_assignment_base
from mcfunction import calc_math

class vector_assignment_scalar_block(vector_assignment_base):
	def __init__(self, line, var, op, expr):
		self.line = line
		self.var = var
		self.op = open
		self.expr = expr
		
	def compile(self, func):
		self.perform_vector_assignment(func)
		
	def compute_assignment(self, func, expr, assignto):
		val_var = calc_math(func, expr)			
		component_val_vars = [val_var for i in range(3)]
		
		return component_val_vars
