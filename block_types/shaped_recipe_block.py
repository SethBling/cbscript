from block_base import block_base
from data_types.shaped_recipe import shaped_recipe

class shaped_recipe_block(block_base):
	def __init__(self, line, recipe_lines, keys, count, item):
		self.line = line
		self.recipe_lines = recipe_lines
		self.keys = keys
		self.count = count
		self.item = item
	
	def compile(self, func):
		count = self.count.get_value(func)
		
		recipe = shaped_recipe(
			self.recipe_lines,
			self.get_keys_with_namespace(func),
			count,
			self.item,
			func.namespace
		)
		
		func.add_recipe(recipe)
		
	def get_keys_with_namespace(self, func):
		keys = []
		for key, type, value in self.keys:
			if type == 'tag' and value in func.item_tags:
				keys.append((key, type, '{}:{}'.format(func.namespace, value)))
			else:
				keys.append((key, type, 'minecraft:{}'.format(value)))
				
		return keys