class array_assignment_block(object):
	def __init__(self, line, name, idxtype, idxval, expr):
		self.line = line
		self.name = name
		self.idxtype = idxtype
		self.idxval = idxval
		self.expr = expr
		
	def compile(self, func):
		if self.name not in func.arrays:
			raise NameError('Tried to assign to undefined array "{}"'.format(self.name))
		
		if self.idxtype == 'Const':
			array_var = func.get_arrayconst_var(self.name, self.idxval)
			
			id = self.expr.compile(func, array_var)
			
			if id == None:
				raise Exception('Unable to compute value for array assignment at line {}'.format(self.line))
				
			if id != array_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(array_var, id))
				
			func.free_scratch(id)
		
		elif self.idxtype == 'Expr':
			val_var = '{}Val'.format(self.name)
			id1 = self.expr.compile(func, val_var)
			
			if id1 == None:
				raise Exception('Unable to compute value for array assignment at line {}'.format(self.line))
			
			idx_var = '{}Idx'.format(self.name)
			
			id2 = self.idxval.compile(func, idx_var)
			if id2 == None:
				raise Exception('Unable to calculate array index at line {}'.format(self.line))
				
			if id1 != val_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(val_var, id1))
			
			if id2 != idx_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(idx_var, id2))
				
			func.add_command('function {}:array_{}_set'.format(func.namespace, self.name.lower()))
			
			func.free_scratch(id1)
			func.free_scratch(id2)