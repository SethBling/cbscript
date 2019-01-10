from const_base import const_base

class scale_expr(const_base):
	def const_value(self, func):
		return func.scale