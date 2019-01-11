from const_base import const_base

class scale_expr(const_base):
	def const_value(self, func):
		if func == None:
			return None
		else:
			return func.scale