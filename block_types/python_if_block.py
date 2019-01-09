import math

class python_if_block(object):
	def __init__(self, line, code, sub, else_sub):
		self.line = line
		self.code = code
		self.sub = sub
		self.else_sub = else_sub
		
	def compile(self, func):
		try:
			condition = eval(self.code, globals(), func.get_python_env())
		except:
			raise Exception('Could not evaluate "{0}" in "if" block at line {1}'.format(self.code, self.line))
	
		if condition:
			if not compile_block(func, self.sub):
				raise Exception('Unable to compile true block for python if block at line {}'.format(self.line))
		else:
			if not compile_block(func, self.else_sub):
				raise Exception('Unable to compile false block for python if block at line {}'.format(self.line))