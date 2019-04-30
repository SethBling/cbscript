from variable_types.scoreboard_var import scoreboard_var

class vector_var_expr(object):
	def __init__(self, vector_id):
		self.vector_id = vector_id
		
	def compile(self, func, assignto):
		return_components = []
		for i in range(3):
			component_name = '_{0}_{1}'.format(self.vector_id, i)
			return_components.append(scoreboard_var('Global', component_name))
			func.register_objective(component_name)
		
		return return_components