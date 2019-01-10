from scalar_expression_base import scalar_expression_base

class (scalar_expression_base):
	def __init__(self, type, expr):
		
	
	def compile(self, func, assignto):
		if self.type == "-":
			id = calc_math(func, self.expr, assignto)
			
			if id == None:
				return None
			
			id = get_modifiable_id(func, id, assignto)

			func.add_constant(-1)
			func.add_command("scoreboard players operation Global {0} *= minus Constant".format(id))
			
			return id
		
		
		print "Unary operation '{0}' isn't implemented.".format(self.type)
		return None