from scalar_expression_base import scalar_expression_base
from mcfunction import get_modifiable_id

class binop_expr(scalar_expression_base):
	def __init__(self, lhs, op, rhs):
		self.lhs = lhs
		self.op = op
		self.rhs = rhs
		
	def compile(self, func, assignto):
		if len(self.op) == 1 and self.op in "+-*/%":
			if self.op in "+*" and self.lhs.const_value(func) != None and self.rhs.const_value(func) == None:
				# Commutative operation which is more efficient with the constant operand on the rhs
				left = self.rhs
				right = self.lhs
			else:
				left = self.lhs
				right = self.rhs
		
			id1 = left.compile(func, assignto)
			if id1 == None:
				print "Unable to compile LHS of binop {0}".format(self.op)
				return None
			
			id1 = get_modifiable_id(func, id1, assignto)
				
			const = right.const_value(func)
			if const != None:
				operand2 = int(const)
					
				if self.op == '+':
					if operand2 >= 0:
						func.add_command('scoreboard players add Global {0} {1}'.format(id1, operand2))
					else:
						func.add_command('scoreboard players remove Global {0} {1}'.format(id1, -operand2))
				elif self.op == '-':
					if operand2 >= 0:
						func.add_command('scoreboard players remove Global {0} {1}'.format(id1, operand2))
					else:
						func.add_command('scoreboard players add Global {0} {1}'.format(id1, -operand2))
				else:
					id2 = func.add_constant(operand2)
					func.add_command('scoreboard players operation Global {0} {1}= {2} Constant'.format(id1, self.op, id2))
			else:
				id2 = right.compile(func, id1)
				if id2 == None:
					print "Unable to compile RHS of binop {0}".format(self.op)
					return None
				
				func.add_operation('Global', id1, self.op+'=', id2)
				func.free_scratch(id2)
			
			return id1
			
		if self.op == "^":
			target = self.lhs.compile(func, assignto)
			
			if target == None:
				print 'Unable to compile exponent for ^'
				return None
			
			right_const = self.rhs.const_value(func)
			if right_const == None:
				print('Exponentiation must have constant operand.')
				return None
				
			power = int(right_const)
			
			if power < 1:
				print "Powers less than 1 are not supported"
				return None
				
			if power == 1:
				return target
			
			newId = func.get_scratch()
			func.add_operation('Global', newId, '=', target)
			
			for i in xrange(power-1):
				func.add_operation('Global', newId, '*=', target)
				
			return newId
			
		print "Binary operation '{0}' isn't implemented".format(self.op)
		return None