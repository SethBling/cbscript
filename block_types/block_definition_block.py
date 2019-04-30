from data_types.relcoords import relcoords

class block_definition_block(object):
	def __init__(self, line, id, items, coords):
		self.line = line
		self.id = id
		self.items = items
		self.coords = coords
		self.paths = {}
		
	def compile(self, func):
		func.add_block_definition(id, self)
		
		for item in self.items:
			self.paths[item.get_name()] = item
		
	def copy_to_objective(self, func, id, coords, macro_args, objective):
		if coords == None:
			coords = self.coords
			
		if id not in self.paths:
			raise ValueError('No path "{}" defined for [{}] at line {}.'.format(self.id, self.line))
			
		self.paths[id].copy_to_objective(func, coords, macro_args, objective)
		
	def copy_from(self, func, id, coords, macro_args, var):
		if coords == None:
			coords = self.coords
			
		if id not in self.paths:
			raise ValueError('No path "{}" defined for [{}] at line {}.'.format(self.id, self.line))
			
		self.paths[id].copy_from(func, coords, macro_args, var)
		
	def get_command(self, func, id, coords, macro_args):
		if coords == None:
			coords = self.coords
			
		if id not in self.paths:
			raise ValueError('No path "{}" defined for [{}] at line {}.'.format(self.id, self.line))
		
		return self.paths[id].get_command(func, coords, macro_args)