class comment_block(block_type):
	def __init__(self, line, text):
		self.line = line
		self.text = text
		if text[0] != '#':
			raise Exception('Comment does not being with "#"')
		
	def compile(self, func):
		func.add_command(self.text)