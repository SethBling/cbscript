from .block_base import block_base
import tellraw

class tell_block(block_base):
	def __init__(self, line, selector, unformatted):
		self.line = line
		self.selector = selector
		self.unformatted = unformatted
		
	def compile(self, func):
		text = tellraw.formatJsonText(func, func.apply_replacements(self.unformatted))
		command = '/tellraw {0} {1}'.format(self.selector, text)
		func.add_command(command)