from cbscript import perform_execute

class execute_block(object):
	def __init__(self, line, exec_items, sub):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		
	def compile(self, func):
		if not perform_execute(func, 'Execute', self.line, self.exec_items, self.sub):
			raise Exception('Unable to compile execute block at line {}'.format(self.line))