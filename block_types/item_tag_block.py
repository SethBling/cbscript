class item_tag_block(object):
	def __init__(self, line, name, items):
		self.line = line
		self.name = name
		self.items = items
		
	def compile(self, func):
		func.register_item_tag(self.name, self.items)