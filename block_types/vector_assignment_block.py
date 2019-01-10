from vector_assignment_base import vector_assignment_base
from mcfunction import calc_vector_math

class vector_assignment_block(vector_assignment_base):
	def __init__(self, line, var, op, expr):
		self.line = line
		self.var = var
		self.op = op
		self.expr = expr
		
	def compile(self, func):
		self.perform_vector_assignment(func, 'VectorAssignment')
		
	def compute_assignment(self, func, expr, assignto):
		component_val_vars = calc_vector_math(func, expr, assignto)
		if component_val_vars == None:
			raise Exception('Unable to compute vector assignment at line {0}'.format(self.line))
				
		return component_val_vars