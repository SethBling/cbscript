from .scalar_expression_base import scalar_expression_base
from variable_types.selector_id_var import selector_id_var

class create_expr(scalar_expression_base):
	def __init__(self, create_block):
		self.create_block = create_block
		
	def compile(self, func, assignto=None):
		func.register_objective('_age')
		func.register_objective('_unique')
		func.register_objective('_id')
		
		func.add_command('scoreboard players set @{} _age 1'.format(self.create_block.atid))
		
		try:
			self.create_block.compile(func)
		except Exception as e:
			print(e)
			raise Exception('Could not run create operation.')
		
		func.add_command('scoreboard players add @{} _age 1'.format(self.create_block.atid))
		
		return selector_id_var('@{}[_age==1,limit=1]'.format(self.create_block.atid))