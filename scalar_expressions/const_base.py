from scalar_expression_base import scalar_expression_base

class const_base(scalar_expression_base):
	def compile(self, func, assignto):
		if assignto != None:
			id = assignto
		else:
			id = func.get_scratch()
			
		func.add_command("scoreboard players set Global {0} {1}".format(id, self.const_value(func)))
		
		return id