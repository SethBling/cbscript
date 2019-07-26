class advancement_definition_block(object):
	def __init__(self, line, name, json):
		self.line = line
		self.name = name
		self.json = json
		
	def compile(self, func):
		json = func.apply_replacements(self.json)
	
		func.add_advancement(self.name, json)