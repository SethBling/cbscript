from block_types.block_base import block_base
from variable_types.scoreboard_var import scoreboard_var
from CompileError import CompileError

class vector_assignment_base(block_base):
	def perform_vector_assignment(self, func):
		var, op, expr = self.var, self.op, self.expr
	
		var_type, var_content = var

		if var_type == 'VAR_COMPONENTS':
			components = var_content
		elif var_type == 'VAR_ID':
			id = var_content
			components = [scoreboard_var('Global', '_{0}_{1}'.format(id, i)) for i in range(3)]
		elif var_type == 'SEL_VAR_ID':
			selector, id = var_content
			components = [scoreboard_var(selector, '_{0}_{1}'.format(id, i)) for i in range(3)]
		elif var_type == 'VAR_CONST':
			raise CompileError('Cannot assign to vector constant at line {}.'.format(self.line))
		
		if op == '=':
			assignto = []
			for var in components:
				component_assignto = var.get_assignto(func)
				if component_assignto == None:
					assignto = None
					break
				else:
					assignto.append(component_assignto)
					
			component_val_vars = self.compute_assignment(func, expr, assignto)
			
			for i in range(3):
				components[i].copy_from(func, component_val_vars[i])
				component_val_vars[i].free_scratch(func)
		else:
			component_val_vars = self.compute_assignment(func, expr, None)
			
			if var_type == 'SEL_VAR_ID':
				selector, id = var_content
				func.get_vector_path(selector, id)
				
			for i in range(3):
				temp_var = components[i].get_scoreboard_var(func)
				rvar = component_val_vars[i].get_scoreboard_var(func)
				func.add_command('scoreboard players operation {} {} {} {} {}'.format(temp_var.selector, temp_var.objective, op, rvar.selector, rvar.objective))
				components[i].copy_from(func, temp_var)
				temp_var.free_scratch(func)
				rvar.free_scratch(func)
				
		if var_type == 'SEL_VAR_ID':
			selector, id = var_content
			func.set_vector_path(selector, id, components)
