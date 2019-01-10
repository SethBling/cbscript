from scalar_expression_base import scalar_expression_base
from mcfunction import get_arrayconst_var

class (scalar_expression_base):
	def __init__(self, name, idx):
		self.name = name
		self.idx = idx
	
	def compile(self, func, assignto):
		array_var = get_arrayconst_var(func, name, idx)
		
		return array_var