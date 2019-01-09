class block_tag_block(object):
	def __init__(self, line, name, blocks):
		self.line = line
		self.name = name
		self.blocks = blocks
		
	def compile(self, func):
		func.register_block_tag(self.name, self.blocks)