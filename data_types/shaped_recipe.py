class shaped_recipe(object):
	def __init__(self, recipe_lines, keys, count, item, group):
		self.recipe_lines = recipe_lines
		self.keys = keys
		self.count = count
		self.item = item
		self.group = group
		
	def get_json_struct(self):
		recipe_struct = {}
		recipe_struct['type'] = 'minecraft:crafting_shaped'
		recipe_struct['group'] = self.group
		recipe_struct['pattern'] = self.recipe_lines
		recipe_struct['key'] = {}
		for key, type, value in self.keys:
			# TODO: check for custom tags
			recipe_struct['key'][key] = {type: value}
			
		recipe_struct['result'] = {
			'item': 'minecraft:' + self.item,
			'count': self.count
		}
			
		return recipe_struct
			
			
	def get_type(self):
		return 'shaped'