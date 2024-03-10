from .block_base import block_base
import collections
from CompileError import CompileError

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
			raise Exception('Unable to compute switch expression at line {}'.format(self.line))

		cases = []
		for case in self.cases_raw:
			type, content, line = case
			if type == 'range':
				vmin, vmax, sub = content
				try:
					vmin = int(vmin.get_value(func))
					vmax = int(vmax.get_value(func))
				except Exception as e:
					print(e)
					raise Exception('Unable to get values of range for case at line {}'.format(line))
					
				cases.append((vmin, vmax, sub, line, None))
			elif type == 'python':
				dollarid, python, sub = content
				try:
					vals = python.get_value(func)
				except:
					raise Exception('Could not evaluate case value at line {}'.format(line))
				
				if not isinstance(vals, collections.Iterable):
					raise Exception('Python "{}" is not iterable at line {}'.format(python, line))

				for val in vals:
					try:
						ival = int(val)
					except:
						print('Value "{}" is not an integer at line {}'.format(val, line))
						return False
					cases.append((ival, ival, sub, line, dollarid))
			else:
				raise CompileError('Unknown switch case type "{}"'.format(type))
		
		cases = sorted(cases, key=lambda case: case[0])
		
		# Check that none of the cases overlap
		prevmax = cases[0][0]-1
		for vmin, vmax, sub, line, dollarid in cases:
			if vmin > vmax:
				raise ValueError('"case {}-{}" has invalid range at line {}'.format(vmin, vmax, line))
				
			if vmin <= prevmax:
				if vmin == vmax:
					rangestr = '{}'.format(vmin)
				else:
					rangestr = '{}-{}'.format(vmin, vmax)
				raise CompileError('"case {}" overlaps another case at line {}'.format(rangestr, line))
				
			prevmax = vmax
			
		if not func.switch_cases(result, cases):
			raise Exception('Unable to compile switch block at line {}'.format(line))
				
		result.free_scratch(func)