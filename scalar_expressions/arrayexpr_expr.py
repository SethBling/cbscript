from scalar_expression_base import scalar_expression_base

class arrayexpr_expr(scalar_expression_base):
	def __init__(self, name, idx_expr):
		self.name = name
		self.idx_expr = idx_expr
	
	def compile(self, func, assignto):
		if self.name not in func.arrays:
			print('Tried to use undefined array "{}"'.format(self.name))
			return None
			
		index_var = '{}Idx'.format(self.name)
		id = self.idx_expr.compile(func, assignto=index_var)
		if id == None:
			return None
		
		if id != index_var:
			func.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
			
		func.add_command('function {}:array_{}_get'.format(func.namespace, self.name.lower()))
		
		func.free_scratch(id)
		
		return '{}Val'.format(self.name)