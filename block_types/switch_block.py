from .block_base import block_base
import collections
from CompileError import CompileError, Pos

class switch_block(block_base):
	def __init__(self, line, expr, cases_raw):
		self.line = line
		self.expr = expr
		self.cases_raw = cases_raw
		
	def compile(self, func):
		if len(self.cases_raw) == 0:
			return
	
		result = self.expr.compile(func, None).get_scoreboard_var(func)
		if result == None:
			raise CompileError(f'Unable to compute switch expression at line {self.line}', Pos(self.line))

		cases = []
		for case in self.cases_raw:
			type, content, line = case
			if type == 'range':
				vmin, vmax, sub = content
				try:
					vmin = int(vmin.get_value(func))
					vmax = int(vmax.get_value(func))
				except Exception as e:
					raise Exception(f'Unable to get values of range for case at line {line}', Pos(self.line)) from e
					
				cases.append((vmin, vmax, sub, line, None))
			elif type == 'python':
				dollarid, python, sub = content
				try:
					vals = python.get_value(func)
				except Exception:
					raise Exception(f'Could not evaluate case value at line {line}') from None
				
				if not isinstance(vals, collections.Iterable):
					raise Exception(f'Python "{python}" is not iterable at line {line}')

				for val in vals:
					try:
						ival = int(val)
					except Exception:
						print(f'Value "{val}" is not an integer at line {line}')
						return False
					cases.append((ival, ival, sub, line, dollarid))
			else:
				raise CompileError(f'Unknown switch case type "{type}"', Pos(self.line))
		
		cases = sorted(cases, key=lambda case: case[0])
		
		# Check that none of the cases overlap
		prevmax = cases[0][0]-1
		for vmin, vmax, sub, line, dollarid in cases:
			if vmin > vmax:
				raise ValueError(f'"case {vmin}-{vmax}" has invalid range at line {line}')
				
			if vmin <= prevmax:
				if vmin == vmax:
					rangestr = f'{vmin}'
				else:
					rangestr = f'{vmin}-{vmax}'
				raise CompileError(f'"case {rangestr}" overlaps another case at line {line}', Pos(self.line))
				
			prevmax = vmax
			
		if not func.switch_cases(result, cases):
			raise Exception(f'Unable to compile switch block at line {line}')
				
		result.free_scratch(func)
