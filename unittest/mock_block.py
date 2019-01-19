class mock_block(object):
	def __init__(self, command = 'mock_block_command'):
		self.command = command
	
	def compile(self, func):
		func.add_command(self.command)