from block_base import block_base
import math

class python_if_block(block_base):
	def __init__(self, line, val, sub, else_sub):
		self.line = line
		self.val = val
		self.sub = sub
		self.else_sub = else_sub
		
	def compile(self, func):
		condition = self.val.get_value(func)
		
		if condition:
			try:
				func.compile_blocks(self.sub)
			except Exception as e:
				print(e.message)
				raise Exception('Unable to compile true block for python if block at line {}'.format(self.line))
		elif self.else_sub != None:
			try:
				func.compile_blocks(self.else_sub)
			except Exception as e:
				print(e.message)
				raise Exception('Unable to compile false block for python if block at line {}'.format(self.line))