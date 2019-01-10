from execute_base import execute_base

class execute_block(execute_base):
	def __init__(self, line, exec_items, sub):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		
	def compile(self, func):
		self.perform_execute(func)
		
	def display_name(self):
		return 'execute'