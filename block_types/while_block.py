from execute_base import execute_base

class while_block(execute_base):
	def __init__(self, line, exec_items, sub):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		
	def compile(self, func):
		self.perform_execute(func, 'While')