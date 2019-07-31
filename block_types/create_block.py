from block_base import block_base

class create_block(block_base):
	def __init__(self, line, atid, relcoords):
		self.line = line
		self.atid = atid
		self.relcoords = relcoords
		
	def compile(self, func):
		if not func.run_create(self.atid, self.relcoords):
			raise Exception('Error creating entity at line {0}'.format(self.line))