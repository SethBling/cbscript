class vector_binop_base(object):
	def __init__(self, lhs, op, rhs):
		self.lhs = lhs
		self.op = op
		self.rhs = rhs
		
	def compile(self, func, assignto):
		return_components = []
		
		left_component_vars = self.lhs.compile(func, assignto)
		if left_component_vars == None:
			return None
			
		for i in range(3):
			if func.is_scratch(left_component_vars[i]):
				return_components.append(left_component_vars[i])
			elif assignto != None:
				if left_component_vars[i] != assignto[i]:
					func.add_command('scoreboard players operation Global {} = Global {}'.format(assignto[i], left_component_vars[i]))
				return_components.append(assignto[i])
			else:
				newId = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, left_component_vars[i]))
				return_components.append(newId)
		
		self.calc_op(func, return_components)
		
		return return_components	