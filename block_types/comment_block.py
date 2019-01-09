class comment_block(object):
	def __init__(self, line, text):
		self.line = line
		self.text = text
		if text[0] != '#':
			raise Exception('Comment does not being with "#"')
		
	def compile(self, func):
		func.add_command(self.text)