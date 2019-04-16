class interpreted_python(object):
	def __init__(self, expr, line):
		self.expr = expr
		self.line = line
		
	def get_value(self, func):
		return func.eval(self.expr, self.line)