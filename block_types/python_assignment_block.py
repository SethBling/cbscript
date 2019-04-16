import math

class python_assignment_block(object):
	def __init__(self, line, id, val):
		self.line = line
		self.id, self.val = id, val
		
	def compile(self, func):
		func.set_dollarid(self.id, self.val.get_value(func))