from block_base import block_base

class loot_table_definition_block(block_base):
	def __init__(self, line, type, name, json):
		self.line = line
		self.type = type
		self.name = name
		self.json = json
		
	def compile(self, func):
		func.add_loot_table(self.name, (self.type, self.json))