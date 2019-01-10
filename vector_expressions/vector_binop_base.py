class vector_binop_base(object):
	def __init__(self, lhs, op, rhs):
		self.lhs = lhs
		self.op = op
		self.rhs = rhs
		
	def evaluate(self, func, assignto):
		return_components = []
		
		left_component_vars = calc_vector_math(func, lhs, assignto)
		if left_component_vars == None:
			return None
			
		for i in range(3):
			if func.is_scratch(left_component_vars[i]):
				return_components.append(left_component_vars[i])
			elif assignto != None and left_component_vars[i] == assignto[i]:
				return_components.append(left_component_vars[i])
			else:
				newId = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, left_component_vars[i]))
				return_components.append(newId)
		
		self.calc_op()
		
		return return_components	