from scalar_expression_base import scalar_expression_base

class selector_expr(scalar_expression_base):
	def __init__(self, selector):
		self.selector = selector
		
	def compile(self, func, assignto):
		if not func.check_single_entity(self.selector):
			print('Selector "{}" does not specify an individual entity.'.format(self.selector))
			return None
	
		func.register_objective('_unique')
		func.register_objective('_id')
		func.add_command('scoreboard players add Global _unique 1')
		func.add_command('execute unless score {0} _id matches 0.. run scoreboard players operation {0} _id = Global _unique'.format(self.selector))
		
		if assignto == None:
			assignto = func.get_scratch()
		func.add_command('scoreboard players operation Global {} = {} _id'.format(assignto, self.selector))
		
		return assignto