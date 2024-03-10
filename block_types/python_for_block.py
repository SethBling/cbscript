from .block_base import block_base
import math
from CompileError import CompileError

class python_for_block(block_base):
	def __init__(self, line, ids, val, sub):
		self.line = line
		self.ids = ids
		self.val = val
		self.sub = sub
		
	def compile(self, func):
		set = self.val.get_value(func)
		
		try:
			iter(set)
		except:
			raise CompileError('"{0}" in "for" block at line {1} is not an iterable set.'.format(set, self.line))

		for v in set:
			if len(self.ids) == 1:
				func.set_dollarid(self.ids[0], v)
			else:
				try:
					v_len = len(v)
				except Exception as e:
					print(e)
					raise CompileError('Set is not a tuple at line {}'.format(self.line))
				if v_len != len(self.ids):
					raise CompileError('Expected {} tuple items at line {}, got {}.'.format(len(self.ids), self.line, v_len))
				for idx in range(v_len):
					func.set_dollarid(self.ids[idx], v[idx])
			try:
				func.compile_blocks(self.sub)
			except CompileError as e:
				print(e)
				raise CompileError('Unable to compile python for block contents at line {}'.format(self.line))
			except:
				print(traceback.format_exc())
				raise CompileError('Unable to compile python for block contents at line {}'.format(self.line))
