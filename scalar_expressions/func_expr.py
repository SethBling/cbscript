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
		
		if efunc == 'sqrt':
			if len(args) <> 1:
				print "sqrt takes exactly 1 argument, received: {}".format(len(args))
				return None
			
			id = args[0].compile(func, None)
			if id == None:
				print 'Unable to compile argument for sqrt'
				return None
			
			guess = num_expr(20).compile(func, None)
			
			if guess == None:
				print 'Unable to compile initial guess for sqrt algorithm'
				return None
				
			for iteration in xrange(15):
				newId = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, id))
				expr = scriptparse.parse("({0}/{1}+{1})/2".format(newId, guess))[1]
				guess = expr.compile(func, None)
				if guess == None:
					print 'Unable to compile guess iteration for sqrt algorithm'
					return None
			
			return scoreboard_var('Global', guess)

		elif efunc == 'abs':
			if len(args) <> 1:
				print "abs takes exactly 1 argument, received: {}".format(len(args))
				return None

			var = args[0].compile(func, assignto).get_modifiable_var(func, assignto)
			
			minus = func.add_constant(-1)
			func.add_command("execute if score {0} {1} matches ..-1 run scoreboard players operation {0} {1} *= {2} Constant".format(var.selector, var.objective, minus))
			
			return var
			
		elif efunc == 'rand':
			if len(args) == 1:
				min = 0
				max = args[0].get_const_value(func)
				
			elif len(args) == 2:
				min = args[0].get_const_value(func)
				max = args[1].get_const_value(func)
				
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

		elif efunc == 'sin' or efunc == 'cos':
			if len(args) <> 1:
				print "{0} takes exactly 1 argument, received: {}".format(efunc, len(args))
				return None
			
			raise NotImplementedError()
			# TODO: Treat args as variables
			
			id = args[0].compile(func, None)
			if id == None:
				print 'Unable to compile argument for {0} function'.format(efunc)
				return None
				
			moddedId2 = func.get_temp_var()
			if efunc == 'sin':
				expr = scriptparse.parse("(({0}%360)+360)%360".format(id))[1]
			else:
				expr = scriptparse.parse("(({0}%360)+450)%360".format(id))[1]
			
			modret = expr.compile(func, moddedId2)
			if modret == None:
				print 'Unable to compile modulus math for {0} function'.format(efunc)
				return None
			if modret != moddedId2:
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(moddedId2, modret))
				
			id = func.get_modifiable_id(id, assignto)
			
			modId = func.get_temp_var()
			func.add_operation('Global', modId, '=', moddedId2)
			c180 = func.add_constant(180)
			func.add_command("scoreboard players operation Global {0} %= {1} Constant".format(modId, c180))
			
			expr = scriptparse.parse("4000*{0}*(180-{0})/(40500-{0}*(180-{0}))".format(modId))[1]
			retId = expr.compile(func, assignto)
			if retId == None:
				print 'Unable to compile estimator for {0} function'.format(efunc)
				return None
			
			func.add_constant(-1)
			func.add_command('execute if score Global {} matches 180.. run scoreboard players operation Global {} *= minus Constant'.format(moddedId2, retId))
			
			func.free_temp_var(modId)
			func.free_temp_var(moddedId2)
			
			return scoreboard_var('Global', retId)
		
		else:
			self.function_call.compile(func)
			
			return scoreboard_var('Global', 'ReturnValue')
		
		return None