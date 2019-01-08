class command_block(block_type):
	def __init__(self, line, text):
		self.line = line
		self.text = text
		
	def compile(self, func):
		func.add_command(self.text)