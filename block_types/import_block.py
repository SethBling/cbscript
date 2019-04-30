import traceback

class import_block(object):
	def __init__(self, line, filename):
		self.line = line
		self.filename = filename
		
	def compile(self, func):
		try:
			func.import_file(self.filename + '.cblib')
		except Exception as e:
			print(traceback.format_exc())
			raise Exception('Importing file "{}" failed at line {}:\n{}'.format(self.filename, self.line, e))