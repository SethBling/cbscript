from block_types.block_base import block_base

class move_block(block_base):
	def __init__(self, line, selector, coords):
		self.line = line
		self.selector = selector
		self.coords = coords
		
	def compile(self, func):
		if self.selector == '@s' or self.selector == '@s[]':
			cmd = 'execute at @s run tp @s {0}'.format(self.coords.get_value(func))
		else:
			cmd = 'execute as {0} at @s run tp @s {1}'.format(self.selector, self.coords.get_value(func))
		
		func.add_command(cmd)
