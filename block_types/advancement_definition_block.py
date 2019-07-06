class advancement_definition_block(object):
	def __init__(self, line, name, json):
		self.line = line
		self.name = name
		self.json = json
		
	def compile(self, func):
		func.add_advancement(self.name, self.json)