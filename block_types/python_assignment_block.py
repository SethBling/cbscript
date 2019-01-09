import math

class python_assignment_block(object):
	def __init__(self, line, id, code):
		self.line = line
		self.id = id
		self.code = code
		
	def compile(self, func):
		try:
			func.set_dollarid(id, eval(self.code, globals(), func.get_python_env()))
		except:
			raise ValueError('Could not evaluate "{0}" at line {1}'.format(self.code, self.line))