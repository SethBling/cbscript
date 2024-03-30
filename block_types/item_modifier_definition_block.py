from .block_base import block_base

class item_modifier_definition_block(block_base):
	def __init__(self, line, name, json):
		self.line = line
		self.name = name
		self.json = json
		
	def compile(self, func):
		func.add_item_modifier(self.name, self.json)