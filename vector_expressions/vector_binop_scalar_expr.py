from vector_binop_base import vector_binop_base

class vector_binop_scalar_expr(vector_binop_base):
	def calc_op(self, func, return_components):
		right_var = self.rhs.compile(func, None)
		if right_var == None:
			return None
		
		for i in range(3):
			func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], self.op, right_var))
			
		func.free_scratch(right_var)
