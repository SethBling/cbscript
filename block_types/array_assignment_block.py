from cbscript import get_arrayconst_var, calc_math

class array_assignment_block(block_type):
	def __init__(self, line, name, idxtype, idxval, expr):
		self.line = line
		self.name = name
		self.idxtype = idxtype
		self.idxval = idxval
		self.expr = expr
		
	def compile(self, func):
		if self.name not in func.arrays:
			print('Tried to assign to undefined array "{}"'.format(self.name))
			return False
		
		if self.idxtype == 'Const':
			array_var = get_arrayconst_var(func, self.name, self.idxval)
			
			id = calc_math(func, self.expr, assignto=array_var)
			
			if id == None:
				raise Exception('Unable to compute value for array assignment at line {}'.format(self.line))
				
			if id != array_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(array_var, id))
				
			func.free_scratch(id)
		
		elif self.idxtype == 'Expr':
			val_var = '{}Val'.format(self.name)
			id1 = calc_math(func, expr, assignto=val_var)
			
			if id1 == None:
				raise Exception('Unable to compute value for array assignment at line {}'.format(self.line))
			
			idx_var = '{}Idx'.format(self.name)
			
			id2 = calc_math(func, idxval, assignto=idx_var)
			if id2 == None:
				raise Exception('Unable to calculate array index at line {}'.format(self.line))
				
			if id1 != val_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(val_var, id1))
			
			if id2 != idx_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(idx_var, id2))
				
			func.add_command('function {}:array_{}_set'.format(func.namespace, self.name.lower()))
			
			func.free_scratch(id1)
			func.free_scratch(id2)