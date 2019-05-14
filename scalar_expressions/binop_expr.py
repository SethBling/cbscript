from scalar_expression_base import scalar_expression_base
class binop_expr(scalar_expression_base):
	def __init__(self, lhs, op, rhs):
		self.lhs = lhs
		self.op = op
		self.rhs = rhs

	def compile(self, func, assignto=None):
		if len(self.op) == 1 and self.op in ['+', '-', '*', '/', '%']:
			left_var = self.lhs.compile(func, assignto)
			temp_var = left_var.get_modifiable_var(func, assignto)
			
			right_var = self.rhs.compile(func, None)
			right_const = right_var.get_const_value(func)
			
			# TODO: handle case where both variables have constant values, return constant result
			
			if right_const and self.op in ['+','-']:
				op = self.op
				
				if right_const < 0:
					right_const = -right_const
					op = {'+':'-', '-':'+'}[self.op]
					
				func.add_command('scoreboard players {} {} {} {}'.format({'+':'add', '-':'remove'}[op], temp_var.selector, temp_var.objective, right_const))
			else:
				right_var = right_var.get_scoreboard_var(func)
				func.add_command('scoreboard players operation {} {} {}= {} {}'.format(temp_var.selector, temp_var.objective, self.op, right_var.selector, right_var.objective))
				
			right_var.free_scratch(func)
			
			return temp_var
			
		if self.op == "^":
			left_var = self.lhs.compile(func, assignto)
			temp_var = left_var.get_modifiable_var(func, assignto)
			
			right_var = self.rhs.compile(func)
			power = int(right_var.get_const_value(func))
			
			if power == None:
				print('Exponentiation must have constant operand.')
				return None
				
			if power < 1:
				print "Powers less than 1 are not supported"
				return None
				
			if power == 1:
				return target
			
			multiplier_obj = func.get_scratch()
			func.add_command('scoreboard players operation Global {} = {} {}'.format(multiplier_obj, temp_var.selector, temp_var.objective))
			
			for i in xrange(power-1):
				func.add_command('scoreboard players operation {} {} *= Global {}'.format(temp_var.selector, temp_var.objective, multiplier_obj))
				
			func.free_scratch(multiplier_obj)
				
			return temp_var
			
		else:	
			print "Binary operation '{0}' isn't implemented".format(self.op)
			return None