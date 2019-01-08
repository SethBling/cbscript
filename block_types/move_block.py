class move_block(block_type):
	def __init__(self, line, selector, coords):
		self.line = line
		self.selector = selector
		self.coords = coords
		
	def compile(self, func):
		if self.selector == '@s':
			cmd = 'execute at @s run tp @s {0}'.format(' '.join(self.coords))
		else:
			cmd = 'execute as {0} at @s run tp @s {1}'.format(self.selector, ' '.join(self.coords))
		
		func.add_command(cmd)