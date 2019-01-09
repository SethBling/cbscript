from cbscript import calc_math, switch_cases, get_line

class switch_block(object):
	def __init__(self, line, expr, cases_raw):
		self.line = line
		self.expr = expr
		self.cases_raw = cases_raw
		
	def compile(self, func):
		result = calc_math(func, self.expr)
		if result == None:
			raise Exception('Unable to compute switch expression at line {}'.format(self.line))

		cases = []
		for case in self.cases_raw:
			type, content = case
			line = get_line(case)
			if type == 'range':
				vmin, vmax, sub = content
				vmin = int(func.apply_replacements(vmin))
				vmax = int(func.apply_replacements(vmax))
				cases.append((vmin, vmax, sub, line, None))
			elif type == 'python':
				dollarid, python, sub = content
				try:
					vals = eval(python, globals(), func.get_python_env())
				except:
					raise Exception('Could not evaluate "{0}" at line {1}'.format(python, line))
				
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
				raise ValueError('Unknown switch case type "{}"'.format(type))
		
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
				raise ValueError('"case {}" overlaps another case at line {}'.format(rangestr, line))
				
			prevmax = vmax
			
		if not switch_cases(func, result, cases):
			return False
				
		func.free_scratch(result)