class print_block(object):
	def __init__(self, line, val):
		self.line = line
		self.val = val
		
	def compile(self, func):
		try:
			print(self.val.get_value(func))
		except Exception as e:
			raise Exception('Unable to get print value at line {}. Exception: "{}"'.format(self.line, e))