from scalar_expression_base import scalar_expression_base

class dot_expr(scalar_expression_base):
	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	
	def compile(self, func, assignto):
		lhs = self.lhs.compile(func, None)
		rhs = self.rhs.compile(func, None)
		
		prods = []
		for i in range(3):
			prod = lhs[i]
			if not func.is_scratch(prod):
				prod = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(prod, lhs[i]))
			func.add_command('scoreboard players operation Global {0} *= Global {1}'.format(prod, rhs[i]))
			
			prods.append(prod)
			
		func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[1]))
		func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[2]))
		
		for i in range(3):
			for vec in [lhs, rhs, prod]:
				if vec[i] != prods[0]:
					func.free_scratch(vec[i])
		
		return prods[0]