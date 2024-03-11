from .block_base import block_base

class pointer_decl_block(block_base):
	def __init__(self, line, id, selector):
		self.line = line
		self.id = id
		self.selector = selector
		
	def compile(self, func):
		func.add_pointer(self.id, self.selector)