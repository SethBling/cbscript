from scalar_expression_base import scalar_expression_base

class arrayconst_expr(scalar_expression_base):
	def __init__(self, name, idx):
		self.name = name
		self.idx = idx
	
	def compile(self, func, assignto):
		array_var = func.get_arrayconst_var(self.name, self.idx)
		
		return array_var