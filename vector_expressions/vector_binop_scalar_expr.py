from .vector_binop_base import vector_binop_base

class vector_binop_scalar_expr(vector_binop_base):
	def calc_op(self, func, return_components):
		right_var = self.rhs.compile(func, None).get_scoreboard_var(func)
		
		for i in range(3):
			func.add_command(f'scoreboard players operation {return_components[i].selector} {return_components[i].objective} {self.op}= {right_var.selector} {right_var.objective}')
			
		right_var.free_scratch(func)
