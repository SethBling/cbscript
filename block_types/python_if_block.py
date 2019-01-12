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
			try:
				func.compile_blocks(self.sub)
			except Exception as e:
				print(e.message)
				raise Exception('Unable to compile true block for python if block at line {}'.format(self.line))
		elif self.else_sub != None:
			try:
				func.compile_blocks(self.else_sub)
			except Excetion as e:
				print(e.message)
				raise Exception('Unable to compile false block for python if block at line {}'.format(self.line))