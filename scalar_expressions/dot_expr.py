from .scalar_expression_base import scalar_expression_base
from variable_types.scoreboard_var import scoreboard_var

class dot_expr(scalar_expression_base):
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	
	def compile(self, func, assignto=None):
		lhs = self.lhs.compile(func, None)
		rhs = self.rhs.compile(func, None)
		
		prods = []
		for i in range(3):
			prod = lhs[i].get_modifiable_var(func, assignto)
			assignto = None
			multiplicand = rhs[i].get_scoreboard_var(func)
			
			func.add_command('scoreboard players operation {} *= {}'.format(prod.selvar, multiplicand.selvar))
			
			prods.append(prod)
			
		func.add_command('scoreboard players operation {0} += {1}'.format(prods[0].selvar, prods[1].selvar))
		func.add_command('scoreboard players operation {0} += {1}'.format(prods[0].selvar, prods[2].selvar))
		
		for i in range(3):
			for var in [lhs[i], rhs[i], prods[i]]:
				if var != prods[0]:
					var.free_scratch(func)
		
		return prods[0]