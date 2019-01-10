from const_base import const_base

class num_expr(const_base):
	def __init__(self, val):
		self.val = val
	
	def const_value(self, func):
		return func.apply_replacements(self.val)