from scalar_expression_base import scalar_expression_base
from variable_types.virtualint_var import virtualint_var
from variable_types.scoreboard_var import scoreboard_var

class unary_expr(scalar_expression_base):
	def __init__(self, type, expr):
		self.type = type
		self.expr = expr
	
	def compile(self, func, assignto=None):
		if self.type == '-':
			var = self.expr.compile(func, assignto)
			
			if var == None:
				return None
			
			const_val = var.get_const_value(func)
			if const_val:
				return virtualint_var(-int(const_val))
			
			temp_var = var.get_modifiable_var(func, assignto)
			minus = func.add_constant(-1)
			func.add_command('scoreboard players operation {} {} *= {} Constant'.format(temp_var.selector, temp_var.objective, minus))
			
			return temp_var
		
		print("Unary operation '{}' isn't implemented.".format(self.type))
		return None