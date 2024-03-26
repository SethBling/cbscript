from .block_base import block_base
import math
from CompileError import CompileError, Pos

class python_tuple_assignment_block(block_base):
	def __init__(self, line, ids, val):
		self.line = line
		self.ids, self.val = ids, val
		
	def compile(self, func):
		val = self.val.get_value(func)
		try:
			val_len = len(val)
		except Exception as e:
			raise CompileError(f'Expression at line {self.line} is not a tuple.', Pos(self.line)) from e
		
		if val_len != len(self.ids):
			raise CompileError(f'Expected {len(self.ids)} values for tuple expression at line {self.line}, got {len(val)}', Pos(self.line))
		
		for idx in range(val_len):
			func.set_dollarid(self.ids[idx], val[idx])
