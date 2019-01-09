class title_block(object):
	def __init__(self, line, subtype, selector, times, unformatted):
		self.line = line
		self.subtype = subtype
		self.selector = selector
		self.times = times
		self.unformatted = unformatted
		
	def compile(self, func):
		if self.times != None:
			func.add_command('/title {} times {}'.format(selector, ' '.join(self.times)))
		
		text = tellraw.formatJsonText(func, self.unformatted)
		command = '/title {} {} {}'.format(self.selector, self.subtype, self.text)
		func.add_command(command)