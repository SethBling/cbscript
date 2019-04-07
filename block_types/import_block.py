class import_block(object):
	def __init__(self, line, filename):
		self.line = line
		self.filename = filename
		
	def compile(self, func):
		try:
			func.import_file(self.filename)
		except Exception as e:
			raise Exception('Importing file "{}" failed at line {}:\n{}'.format(self.filename, self.line, e))