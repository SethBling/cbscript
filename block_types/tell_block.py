import tellraw

class tell_block(object):
	def __init__(self, line, selector, unformatted):
		self.line = line
		self.selector = selector
		self.unformatted = unformatted
		
	def compile(self, func):
		text = tellraw.formatJsonText(func, self.unformatted)
		command = '/tellraw {0} {1}'.format(self.selector, text)
		func.add_command(command)