from scalar_expression_base import scalar_expression_base

class unary_expr(scalar_expression_base):
	def __init__(self, type, expr):
		self.type = type
		self.expr = expr
	
	def compile(self, func, assignto):
		if self.type == "-":
			id = self.expr.compile(func, assignto)
			
			if id == None:
				return None
			
			id = func.get_modifiable_id(id, assignto)

			func.add_constant(-1)
			func.add_command("scoreboard players operation Global {0} *= minus Constant".format(id))
			
			return id
		
		
		print "Unary operation '{0}' isn't implemented.".format(self.type)
		return None