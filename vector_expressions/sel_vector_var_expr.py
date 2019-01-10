class sel_vector_var_expr(object):
	def __init__(self, sel, id):
		self.sel = sel
		self.id = id
		
	def compile(self, func, assignto):
		return_components = []
		for i in range(3):
			if assignto != None:
				return_components.append(assignto[i])
			else:
				return_components.append(func.get_scratch())
		
		if not func.get_vector_path(self.sel, self.id, return_components):
			for i in range(3):
				var = '_{0}_{1}'.format(self.id, i)
				func.register_objective(var)
				func.add_command('scoreboard players operation Global {0} = {1} {2}'.format(return_components[i], self.sel, var))
		
		return return_components