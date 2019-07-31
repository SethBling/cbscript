from block_base import block_base

class selector_assignment_block(block_base):
	def __init__(self, line, id, fullselector):
		self.line = line
		self.id = id
		self.fullselector = fullselector
		
	def compile(self, func):
		func.set_atid(self.id, self.fullselector)