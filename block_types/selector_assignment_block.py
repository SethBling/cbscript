class selector_assignment_block(object):
	def __init__(self, line, id, fullselector):
		self.line = line
		self.id = id
		self.fullselector = fullselector
		
	def compile(self, func):
		func.set_atid(id, fullselector)