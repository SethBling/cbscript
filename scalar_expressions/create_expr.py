from scalar_expression_base import scalar_expression_base

class create_expr(scalar_expression_base):
	def __init__(self, create_block):
		self.create_block = create_block
		
	def compile(self, func, assignto):
		func.register_objective('_age')
		func.register_objective('_unique')
		func.register_objective('_id')
		
		func.add_command('scoreboard players add @e _age 1')
		
		try:
			self.create_block.compile(func)
		except Exception as e:
			print(e)
			print('Could not run create operation.')
			return None
		
		func.add_command('scoreboard players add @e _age 1')
		func.add_command('scoreboard players add Global _unique 1')
		func.add_command('scoreboard players operation @{0}[_age==1] _id = Global _unique'.format(self.create_block.atid))
		if assignto == None:
			assignto = func.get_scratch()
		func.add_command('scoreboard players operation Global {} = Global _unique'.format(assignto))
		
		return assignto
