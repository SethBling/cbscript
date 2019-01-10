from vector_binop_base import vector_binop_base

class vector_binop_vector_expr(vector_binop_base):
	def calc_op(self, func, return_components):
		right_component_vars = calc_vector_math(func, self.rhs)
		
		if right_component_vars == None:
			return None
			
		for i in range(3):
			func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], self.op, right_component_vars[i]))
			func.free_scratch(right_component_vars[i])