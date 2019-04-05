class mock_block(object):
	def __init__(self, command = 'mock_block_command', raiseException = False, line=0):
		self.command = command
		self.raiseException = raiseException
		self.line = line
	
	def compile(self, func):
		if self.raiseException:
			raise Exception('mock exception')
		func.add_command(self.command)