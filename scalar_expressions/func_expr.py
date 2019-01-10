from scalar_expression_base import scalar_expression_base
from num_expr import num_expr

class func_expr(scalar_expression_base):
	def __init__(self, function_call):
		self.function_call = function_call
	
	def compile(self, func, assignto):
		efunc = self.function_call.dest
		args = self.function_call.args
		
		if efunc == 'sqrt':
			if len(args) <> 1:
				print "sqrt takes exactly 1 argument, received: {0}".format(args)
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
				guess = calc_math(func, scriptparse.parse("({0}/{1}+{1})/2".format(newId, guess))[1])
				if guess == None:
					print 'Unable to compile guess iteration for sqrt algorithm'
					return None
			
			return guess

		elif efunc == 'abs':
			if len(args) <> 1:
				print "abs takes exactly 1 argument, received: {0}".format(args)
				return None

			id = calc_math(func, args[0], assignto=assignto)
			if id == None:
				print 'Unable to compile argument for abs function'
				return None
			
			id = get_modifiable_id(func, id, assignto)
		
			func.add_constant(-1)
			func.add_command("execute if score Global {0} matches ..-1 run scoreboard players operation Global {0} *= minus Constant".format(id))
			
			return id
			
		elif efunc == 'rand':
			if len(args) == 1:
				min = 0
				if args[0][0] == 'NUM':
					max = func.apply_environment(args[0][1])
					if not isNumber(max):
						print "Argument '{0}' to rand is not an integer.".format(args[0][1])
						return None
					max = int(max)
				else:
					print "Function 'rand' accepts only integer arguments."
					return None
			elif len(args) == 2:
				if args[0][0] == 'NUM':
					min = func.apply_environment(args[0][1])
					if not isNumber(min):
						print "Argument '{0}' to rand is not an integer.".format(args[0][1])
						return None
					min = int(min)
				else:
					print "Function 'rand' accepts only integer arguments."
					return None
				if args[1][0] == 'NUM':
					max = func.apply_environment(args[1][1])
					if not isNumber(max):
						print "Argument '{0}' to rand is not an integer.".format(args[1][1])
						return None
					max = int(max)

				else:
					print "Function 'rand' accepts only integer arguments."
					return None
			else:
				print "rand takes 1 or 2 arguments, received: {0}".format(args)
				return None
				
			span = max - min
			
			if span <= 0:
				print("rand must have a range greater than 0. Provided {0} to {1}.".format(min, max))
				return None

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
				
			return id

		elif efunc == 'sin' or efunc == 'cos':
			if len(args) <> 1:
				print "{0} takes exactly 1 argument, received: {1}".format(efunc, args)
				return None
			
			id = args[0].compile(func, None)
			if id == None:
				print 'Unable to compile argument for {0} function'.format(efunc)
				return None
				
			moddedId2 = func.get_temp_var()
			if efunc == 'sin':
				modret = calc_math(func, scriptparse.parse("(({0}%360)+360)%360".format(id))[1], assignto=moddedId2)
			else:
				modret = calc_math(func, scriptparse.parse("(({0}%360)+450)%360".format(id))[1], assignto=moddedId2)
			if modret == None:
				print 'Unable to compile modulus math for {0} function'.format(efunc)
				return None
			if modret != moddedId2:
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(moddedId2, modret))
				
			id = get_modifiable_id(func, id, assignto)
			
			modId = func.get_temp_var()
			func.add_operation('Global', modId, '=', moddedId2)
			c180 = func.add_constant(180)
			func.add_command("scoreboard players operation Global {0} %= {1} Constant".format(modId, c180))
			
			parsed = scriptparse.parse("4000*{0}*(180-{0})/(40500-{0}*(180-{0}))".format(modId))
			retId = calc_math(func, parsed[1], assignto=assignto)
			if retId == None:
				print 'Unable to compile estimator for {0} function'.format(efunc)
				return None
			
			func.add_constant(-1)
			func.add_command("/execute if score Global {0} matches 180.. run scoreboard players operation Global {1} *= minus Constant".format(moddedId2, retId))
			
			func.free_temp_var(modId)
			func.free_temp_var(moddedId2)
			
			return retId
		
		else:
			self.function_call.compile(func)
			
			return "ReturnValue"
		
		return None