class create_block(object):
	def __init__(self, line, atid, relcoords):
		self.line = line
		self.atid = atid
		self.relcoords = relcoords
		
	def compile(self, func):
		if not func.run_create(self.atid, self.relcoords):
			raise Exception('Error creating entity at line {0}'.format(self.line))