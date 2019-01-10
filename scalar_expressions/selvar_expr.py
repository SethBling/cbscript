from scalar_expression_base import scalar_expression_base

class selvar_expr(scalar_expression_base):
	def __init__(self, sel, var):
		self.sel = sel
		self.var = var
		
	def compile(self, func, assignto):
		func.register_objective(self.var)
		
		func.get_path(self.sel, self.var)
		
		if assignto != None:
			newId = assignto
		elif self.sel != 'Global':
			newId = func.get_scratch()
		else:
			newId = self.var
		
		if self.sel != 'Global' or newId != self.var:
			func.add_command("scoreboard players operation Global {0} = {1} {2}".format(newId, self.sel, self.var))
		
		return newId