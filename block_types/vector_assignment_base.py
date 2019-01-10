from mcfunction import get_variable, set_variable

class vector_assignment_base(object):
	def perform_vector_assignment(self, func):
		var, op, expr = self.var, self.op, self.expr
	
		var_type, var_content = var
		
		if op == '=':
			modify = False
		else:
			modify = True
		
		if var_type == 'VAR_COMPONENTS':
			# Get and initialize the 3 variables
			components = var_content
			component_vars = []
			
			for i in range(3):
				sel, id = get_variable(func, components[i], initialize = modify)
				component_vars.append((sel, id))
		
		if not modify:
			# Not modifying the variable, so assign straight to it
			assignto = []
			if var_type == 'VAR_ID':
				for i in range(3):
					var_name = '_{0}_{1}'.format(var_content, i)
					assignto.append(var_name)
			elif var_type == 'SEL_VAR_ID':
				assignto = None
			elif var_type == 'VAR_COMPONENTS':
				for sel, id in component_vars:
					if sel == 'Global':
						assignto.append(id)
					else:
						assignto = None
						break
		else:
			assignto = None
		
		component_val_vars = self.compute_assignment(func, expr, assignto)
		
		if var_type == 'VAR_ID':
			for i in range(3):
				var_name = '_{0}_{1}'.format(var_content, i)
				if var_name != component_val_vars[i]:
					func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(var_name, op, component_val_vars[i]))
				func.register_objective(var_name)
				
		elif var_type == 'SEL_VAR_ID':
			sel, id = var_content

			if op != '=':
				temp_vars = func.get_scratch_vector()
				if func.get_vector_path(sel, id, temp_vars):
					for i in range(3):
						func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(temp_vars[i], op, component_val_vars[i]))
				
					component_val_vars = temp_vars
				else:
					for var in temp_vars:
						func.free_scratch(var)
				
			if not func.set_vector_path(sel, id, component_val_vars):
				for i in range(3):
					var = '_{0}_{1}'.format(id, i)
					func.register_objective(var)
					func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, var, op, component_val_vars[i]))

		elif var_type == 'VAR_COMPONENTS':
			components = var_content
		
			for i in range(3):
				sel, id = component_vars[i]
				var = components[i]
				
				if sel != 'Global' or id != component_val_vars[i]:
					func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, id, op, component_val_vars[i]))
					
				set_variable(func, var)
				
		else:
			raise Exception('Unknown vector variable type "{0}" at line {1}'.format(var_type, self.line))

		for i in range(3):
			func.free_scratch(component_val_vars[i])