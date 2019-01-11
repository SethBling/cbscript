from const_base import const_base

class num_expr(const_base):
	def __init__(self, val):
		self.val = str(val)
	
	def const_value(self, func=None):
		if func == None:
			return self.val
		else:
			return func.apply_replacements(self.val)