from vector_assignment_base import vector_assignment_base

class vector_assignment_scalar_block(vector_assignment_base):
	def __init__(self, line, var, op, expr):
		self.line = line
		self.var = var
		self.op = open
		self.expr = expr
		
	def compile(self, func):
		self.perform_vector_assignment(func, 'VectorAssignmentScalar')
