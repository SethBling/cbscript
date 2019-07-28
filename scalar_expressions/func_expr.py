from scalar_expression_base import scalar_expression_base
from variable_types.scoreboard_var import scoreboard_var
from environment import isInt
import math

def factor(n):
	i = 2
	limit = math.sqrt(n)    
	while i <= limit:
	  if n % i == 0:
		yield i
		n = n / i
		limit = math.sqrt(n)   
	  else:
		i += 1
	if n > 1:
		yield n

class func_expr(scalar_expression_base):
	def __init__(self, function_call):
		self.function_call = function_call
	
	def compile(self, func, assignto=None):
		import scriptparse
		
		efunc = self.function_call.dest
		args = self.function_call.args
		
		if efunc == 'rand':
			if len(args) == 1:
				min = 0
				max = args[0].compile(func, None).get_const_value(func)
				
			elif len(args) == 2:
				min = args[0].compile(func, None).get_const_value(func)
				max = args[1].compile(func, None).get_const_value(func)
				
			else:
				raise ValueError('rand takes 1 or 2 arguments, received: {}'.format(args))
				return None
				
			if min == None or not isInt(min) or max == None or not isInt(max):
				raise TypeError('Arguments to rand() must be integers.')
				
			min = int(min)
			max = int(max)
				
			span = max - min
			
			if span <= 0:
				raise ValueError('rand() must have a range greater than 0. Provided {0} to {1}.'.format(min, max))

			id = func.get_scratch()
			func.add_command("scoreboard players set Global {0} 0".format(id))
			
			first = True
			for f in factor(span):
				func.allocate_rand(f)
				
				if first:
					first = False
				else:
					c = func.add_constant(f)
					func.add_command("scoreboard players operation Global {0} *= {1} Constant".format(id, c))
				
				rand_stand = '@e[type=armor_stand, {0} <= {1}, limit=1, sort=random]'.format(func.get_random_objective(), f-1)
				rand_stand = func.apply_environment(rand_stand)
				func.add_command("scoreboard players operation Global {0} += {1} {2}".format(id, rand_stand, func.get_random_objective()))
			
			if min > 0:
				func.add_command("scoreboard players add Global {0} {1}".format(id, min))
			if min < 0:
				func.add_command("scoreboard players remove Global {0} {1}".format(id, -min))
				
			return scoreboard_var('Global', id)

		else:
			self.function_call.compile(func)
			
			return scoreboard_var('Global', 'ReturnValue')
		
		return None