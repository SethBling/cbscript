class selector_assignment_block(block_type):
	def __init__(self, line, id, fullselector):
		self.line = line
		self.id = id
		self.fullselector = fullselector
		
	def compile(self, func):
		func.set_atid(id, fullselector)