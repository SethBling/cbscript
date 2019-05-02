class CompileError(Exception):
	def __init__(self, text):
		super(Exception, self).__init__(text)