class command_block(object):
	def __init__(self, line, text):
		self.line = line
		self.text = text
		
	def compile(self, func):
		func.add_command(self.text)