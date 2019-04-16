class vector_here_expr(object):
	def __init__(self, scale):
		self.scale = scale

	def compile(self, func, assignto):
		if self.scale == None:
			scale = func.scale
		else:
			scale = self.scale.get_value(func)
		
		func.register_objective('_age')
		func.add_command('scoreboard players add @e _age 1')
		func.add_command('summon area_effect_cloud')
		func.add_command('scoreboard players add @e _age 1')
		
		return_components = []
		for i in range(3):
			if assignto == None:
				return_components.append(func.get_scratch())
			else:
				return_components.append(assignto[i])
		
			func.add_command('execute store result score Global {0} run data get entity @e[_age==1,limit=1] Pos[{1}] {2}'.format(return_components[i], i, scale))
		
		func.add_command('/kill @e[_age==1]')
		
		return return_components