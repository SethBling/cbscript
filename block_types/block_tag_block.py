from block_base import block_base

class block_tag_block(block_base):
	def __init__(self, line, name, blocks):
		self.line = line
		self.name = name
		self.blocks = blocks
		
	def compile(self, func):
		func.register_block_tag(self.name, self.blocks)