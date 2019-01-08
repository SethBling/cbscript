from cbscript import compile_block

class python_for_block(block_type):
	def __init__(self, line, id, code, sub):
		self.line = line
		self.id = id
		self.code = code
		self.sub = sub
		
	def compile(self, func):
		try:
			set = eval(self.code, globals(), func.get_python_env())
		except:
			raise ValueError('Could not evaluate "{0}" in "for" block at line {1}'.format(self.code, self.line))
		
		try:
			iter(set)
		except:
			raise ValueError('"{0}" in "for" block at line {1} is not an iterable set.'.format(self.code, self.line))

		for v in set:
			func.set_dollarid(self.id, v)
			compile_block(func, self.sub)