from cbscript import calc_math, get_variable, set_variable, run_create

class scoreboard_assignment_block(object):
	def __init__(self, line, var, op, expr):
		self.line = line
		self.var = var
		self.op = op
		self.expr = expr
		
	def compile(self, func):
		var, op, expr = self.var, self.op, self.expr
			
		if op in ['+=', '-=', '*=', '/=', '%=']:
			modify = True
		else:
			modify = False
		
		(raw_selector, objective) = get_variable(func, var, initialize = modify)
		
		selector = func.apply_environment(raw_selector)
		
		if op in ['+=', '-=', '='] and expr[0] == 'NUM' or expr[0] == 'SCALE':
			if expr[0] == 'NUM':
				operand = func.apply_environment(expr[1])
			elif expr[0] == 'SCALE':
				operand = func.scale
			
			if not isNumber(operand):
				raise TypeError("Unable to apply {0} to {1} at line {2}.".format(op, operand, self.line))
				
			operand = int(operand)
			
			if op == '+=':
				opword = 'add'
			elif op == '-=':
				opword = 'remove'
			elif op == '=':
				opword = 'set'
			else:
				raise ValueError('Unknown selector arithmetic operation: "{0}" at line {1}'.format(op, self.line))
				
			func.add_command('/scoreboard players {0} {1} {2} {3}'.format(opword, selector, objective, operand))
			
		elif expr[0] == 'NUM' or expr[0] == 'SCALE':
			if expr[0] == 'NUM':
				operand = func.apply_environment(expr[1])
			elif expr[0] == 'SCALE':
				operand = func.scale
			
			if not isNumber(operand):
				raise TypeError("Unable to apply {0} to {1} at line {2}.".format(op, operand, self.line))
				
			operand = int(operand)
		
			id2 = func.add_constant(operand)
			command = "/scoreboard players operation {0} {1} {2} {3} {4}".format(selector, objective, op, id2, "Constant")
			
			func.add_command(command)
			
			# Is this redundant with the call at the end of the function?
			set_variable(func, var)
			
		elif op == '=' and expr[0] == 'Selector':
			target = expr[1]
			
			if not func.check_single_entity(target):
				raise ValueError('Selector "{0}" not limited to a single entity at line {1}'.format(target, self.line))
		
			self.global_context.register_objective('_unique')
			self.global_context.register_objective('_id')
			func.add_command('scoreboard players add Global _unique 1')
			func.add_command('execute unless score {0} _id matches 0.. run scoreboard players operation {0} _id = Global _unique'.format(target))
			func.add_command('scoreboard players operation {0} {1} = {2} _id'.format(selector, objective, target))
			
		elif op == '=' and expr[0] == 'Create':
			atid, relcoords = expr[1]
			
			self.global_context.register_objective('_age')
			self.global_context.register_objective('_unique')
			self.global_context.register_objective('_id')
			
			func.add_command('scoreboard players add @e _age 1')
							
			if not run_create(func, atid, relcoords):
				raise Exception('Error creating entity at line {0}'.format(self.line))
				
			func.add_command('scoreboard players add @e _age 1')
			func.add_command('scoreboard players add Global _unique 1')
			func.add_command('scoreboard players operation @{0}[_age==1] _id = Global _unique'.format(atid))
			func.add_command('scoreboard players operation {0} {1} = Global _unique'.format(selector, objective))
			
		else:
			assignto = None
			if op == '=' and objective != 'ReturnValue' and selector == 'Global':
				assignto = objective
				
			if op != '=':
				func.get_path(raw_selector, objective)
				
			result = calc_math(func, expr, assignto=assignto)

			if result == None:
				raise Exception('Unable to compile assignment operand for {0} {1} {2} at line {3}.'.format(selector, objective, op, self.line))
				
			if selector != 'Global' or result != objective or op != '=':
				func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(selector, objective, op, result))
				
			func.free_scratch(result)

		set_variable(func, var)