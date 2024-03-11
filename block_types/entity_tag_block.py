from .block_base import block_base

class entity_tag_block(block_base):
	def __init__(self, line, name, entities):
		self.line = line
		self.name = name
		self.entities = entities
		
	def compile(self, func):
		func.register_entity_tag(self.name, self.entities)