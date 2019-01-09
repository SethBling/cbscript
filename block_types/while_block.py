class while_block(object):
	def __init__(self, line, exec_items, sub):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		
	def compile(self, func):
		if not func.perform_execute('While', self.line, self.exec_items, self.sub):
			raise Exception('Unable to compile while block at line {}'.format(self.line))