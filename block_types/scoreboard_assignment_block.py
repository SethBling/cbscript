from mcfunction import isNumber

class scoreboard_assignment_block(object):
	def __init__(self, line, assignment):
		self.var, self.op, self.expr = assignment
		self.line = line
		
	def compile(self, func):
		var, op, expr = self.var, self.op, self.expr
			
		if op in ['+=', '-=', '*=', '/=', '%=']:
			modify = True
		else:
			modify = False
		
		(raw_selector, objective) = func.get_variable(var, initialize = modify)
		
		selector = func.apply_environment(raw_selector)
		
		const_val = expr.const_value(func)
		
		if const_val != None:
			try:
				operand = int(const_val)
			except:
				raise TypeError('Assignment operand "{}" does not evaluate to an integer at line {}'.format(self.line))
			
			if op in ['+=', '-=', '=']:
				if op == '+=':
					opword = 'add'
				elif op == '-=':
					opword = 'remove'
				elif op == '=':
					opword = 'set'
				else:
					raise ValueError('Unknown selector arithmetic operation: "{0}" at line {1}'.format(op, self.line))
					
				func.add_command('/scoreboard players {0} {1} {2} {3}'.format(opword, selector, objective, operand))
				
			else:			
				id2 = func.add_constant(operand)
				command = "/scoreboard players operation {0} {1} {2} {3} {4}".format(selector, objective, op, id2, "Constant")
				
				func.add_command(command)
				
				# Is this redundant with the call at the end of the function?
				func.set_variable(var)
		else:
			assignto = None
			if op == '=' and objective != 'ReturnValue' and selector == 'Global':
				assignto = objective
				
			if op != '=':
				func.get_path(raw_selector, objective)
				
			result = expr.compile(func, assignto)

			if result == None:
				raise Exception('Unable to compile assignment operand for {0} {1} {2} at line {3}.'.format(selector, objective, op, self.line))
				
			if selector != 'Global' or result != objective or op != '=':
				func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(selector, objective, op, result))
				
			func.free_scratch(result)

		func.set_variable(var)