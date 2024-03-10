from .block_base import block_base

class move_block(block_base):
	def __init__(self, line, selector, coords):
		self.line = line
		self.selector = selector
		self.coords = coords
		
	def compile(self, func):
		if self.selector == '@s' or self.selector == '@s[]':
			cmd = f'execute at @s run tp @s {self.coords.get_value(func)}'
		else:
			cmd = f'execute as {self.selector} at @s run tp @s {self.coords.get_value(func)}'
		
		func.add_command(cmd)
