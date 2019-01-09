from cbscript import run_create

class create_block(object):
	def __init__(self, line, atid, text):
		self.line = line
		self.atid = atid
		self.text = text
		
	def compile(self, func):
		if not run_create(func, self.atid, self.relcoords):
			raise Exception('Error creating entity at line {0}'.format(self.line))
			