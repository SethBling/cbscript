from mcfunction import calc_math

class for_index_block(object):
	def __init__(self, line, var, fr, to, by, sub):
		self.line = line
		self.var = var
		self.fr = fr
		self.to = to
		self.by = by
		self.sub = sub
		
	def compile(self, func):
		var, fr, to, by, sub = self.var, self.fr, self.to, self.by, self.sub
		
		func.register_objective(var)
		
		from_var = calc_math(func, fr, var)
		if from_var != var:
			func.add_command('scoreboard players operation Global {0} = Global {1}'.format(var, from_var))

		to_scratch = func.get_scratch()
		to_var = calc_math(func, to, to_scratch)
		if to_var != to_scratch:
			func.add_command('scoreboard players operation Global {0} = Global {1}'.format(to_scratch, to_var))
			
		if by != None:
			by_scratch = func.get_scratch()
			by_var = calc_math(func, by, by_scratch)
			if by_var != by_scratch:
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(by_scratch, by_var))
				
		unique = func.get_unique_id()
		loop_func_name = 'for{0:03}_ln{1}'.format(unique, self.line)

		loop_func = func.create_child_function()
		func.register_function(loop_func_name, loop_func)	
		
		if not loop_func.compile_blocks(sub):
			raise Exception('Unable to compile for block at line {}'.format(self.line))
		
		if by == None:
			continue_command = 'execute if score Global {0} <= Global {1} run function {2}:{3}'.format(var, to_scratch, func.namespace, loop_func_name)
			func.add_command(continue_command)
			loop_func.add_command('scoreboard players add Global {0} 1'.format(var))
			loop_func.add_command(continue_command)
		else:
			continue_negative_command = 'execute if score Global {0} matches ..-1 if score Global {1} >= Global {2} run function {3}:{4}'.format(by_scratch, var, to_scratch, func.namespace, loop_func_name)
			continue_positive_command = 'execute if score Global {0} matches 1.. if score Global {1} <= Global {2} run function {3}:{4}'.format(by_scratch, var, to_scratch, func.namespace, loop_func_name)
			func.add_command(continue_negative_command)
			func.add_command(continue_positive_command)
			loop_func.add_command('scoreboard players operation Global {0} += Global {1}'.format(var, by_scratch))
			loop_func.add_command(continue_negative_command)
			loop_func.add_command(continue_positive_command)				
			
		func.free_scratch(to_scratch)
		if by != None:
			func.free_scratch(by_scratch)
