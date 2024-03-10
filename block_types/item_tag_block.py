from .block_base import block_base

class item_tag_block(block_base):
	def __init__(self, line, name, items):
		self.line = line
		self.name = name
		self.items = items
		
	def compile(self, func):
		func.register_item_tag(self.name, self.items)