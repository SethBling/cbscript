from selector_definition import selector_definition
import math

line_numbers = []

def get_line(parsed):
	for obj, line in line_numbers:
		if obj is parsed:
			return line
			
	return 'Unknown'


def compile_section(section, environment):
	type, name, template_params, params, lines = section

	if type == 'function':
		f = mcfunction(environment.clone(new_function_name = name), True, params)
	else:
		f = mcfunction(environment.clone(new_function_name = name))
		
	environment.register_function(name, f)

	if type == 'clock':
		environment.register_clock(name)
		
	if not f.compile_blocks(lines):
		return False
			
	return True

def switch_cases(func, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
	if len(cases) == 1:
		vmin, vmax, sub, line, dollarid = cases[0]
		if dollarid != None:
			func.set_dollarid(dollarid, vmin)
		if not func.compile_blocks(sub):
			return False
	else:
		for q in range(4):
			imin = q * len(cases) / 4
			imax = (q+1) * len(cases) / 4
			if imin == imax:
				continue
		
			vmin = cases[imin][0]
			vmax = cases[imax-1][1]
			line = cases[imin][3]
			
			sub_cases = cases[imin:imax]
			sub_env = func.clone_environment()
			case_func = mcfunction(sub_env)
			
			if len(sub_cases) == 1:
				vmin, vmax, sub, line, dollarid = sub_cases[0]
				if dollarid != None:
					case_func.set_dollarid(dollarid, vmin)
				if not case_func.compile_blocks(sub):
					return False
					
				single_command = case_func.single_command()
				if single_command != None:
					if single_command.startswith('/'):
						single_command = single_command[1:]
						
					func.add_command('execute if score Global {} matches {}..{} run {}'.format(var, vmin, vmax, single_command))
				else:
					unique = func.get_unique_id()

					if vmin == vmax:
						case_name = '{}{}_{:03}_ln{}'.format(case_func_name, vmin, unique, line)
					else:
						case_name = '{}{}-{}_{:03}_ln{}'.format(case_func_name, vmin, vmax, unique, line)
						
					func.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, func.namespace, case_name))
					func.register_function(case_name, case_func)
			else:
				unique = func.get_unique_id()
				case_name = '{}{}-{}_{:03}_ln{}'.format(switch_func_name, vmin, vmax, unique, line)
				func.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, func.namespace, case_name))
				func.register_function(case_name, case_func)
			
				if not switch_cases(case_func, var, sub_cases):
					return False
			
	return True

def combine_selectors(selector, qualifiers):
	if selector[-1] <> ']':
		return selector + qualifiers
	else:
		return selector[:-1] + "," + qualifiers[1:]

def isNumber(s):
	try:
		val = float(s)
		
		if math.isinf(val):
			return False
			
		if math.isnan(val):
			return False
		
		return True
	except ValueError:
		return False
		
	except TypeError:
		return False
		
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

# Takes a scoreboard objective and returns a (potentially different)
# scoreboard objective which can be freely modified.
def get_modifiable_id(func, id, assignto):
	if assignto != None:
		if id != assignto:
			func.add_operation('Global', assignto, '=', id)
			id = assignto
	elif not func.is_scratch(id):
		newId = func.get_scratch()
		func.add_operation('Global', newId, '=', id)
		id = newId
		
	return id
	
def get_arrayconst_var(func, name, idxval):
	if name not in func.arrays:
		print('Tried to use undefined array "{}"'.format(name))
		return None
		
	from_val, to_val = func.arrays[name]
	
	index = int(func.apply_replacements(idxval))
	
	if index < from_val or index >= to_val:
		if from_val == 0:
			print('Tried to index {} outside of array {}[{}]'.format(index, name, to_val))
		else:
			print('Tried to index {} outside of array {}[{} to {}]'.format(index, name, from_val, to_val))

	return '{}{}'.format(name, index)
	
def get_variable(func, variable, initialize):
	type, content = variable
	
	if type == 'Var':
		id, var = content
		
		if initialize:
			func.get_path(id, var)
			
		func.register_objective(var)
		
		return content
		
	if type == 'ArrayConst':
		name, idxval = content
		
		array_var = get_arrayconst_var(func, name, idxval)
		
		return 'Global', array_var
		
	if type == 'ArrayExpr':
		name, idx_expr = content
		
		if name not in func.arrays:
			print('Tried to use undefined array "{}"'.format(name))
			return None
			
		index_var = '{}Idx'.format(name)
		id = calc_math(func, idx_expr, assignto=index_var)
		if id == None:
			raise Exception('Unable to calculate array "{}" index'.format(name))
		
		if id != index_var:
			func.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
			
		if initialize:
			func.add_command('function {}:array_{}_get'.format(func.namespace, name.lower()))
		
		func.free_scratch(id)
		
		return 'Global', '{}Val'.format(name)
	
	else:
		raise Exception('Tried to get unknown variable type "{}"'.format(type))

		
def set_variable(func, variable):
	type, content = variable
	
	if type == 'Var':
		id, var = content
		func.set_path(id, var)
		
	elif type == 'ArrayExpr':
		name, idx_expr = content
		func.add_command('function {}:array_{}_set'.format(func.namespace, name.lower()))
	
def evaluate_params(func, params):
	results = []
	for p in range(len(params)):
		param_name = 'Param{0}'.format(p)
		val = calc_math(func, params[p])
		func.add_operation('Global', 'Param{0}'.format(p), '=', val)
	
	return True

def calc_vector_math(func, expr, assignto=None):
	type, content = expr
	
	if type == 'VECTOR':
		exprs = content
		vars = []
		for i in range(3):
			if assignto == None:
				var = calc_math(func, exprs[i])
			else:
				var = calc_math(func, exprs[i], assignto[i])
				
			if var == None:
				return None
				
			vars.append(var)
		
		return vars
	
	elif type == 'VECTOR_VAR':
		vector_id = content
		
		return_components = []
		for i in range(3):
			component_name = '_{0}_{1}'.format(vector_id, i)
			return_components.append(component_name)
			func.register_objective(component_name)
		
		return return_components
		
	elif type == 'SEL_VECTOR_VAR':
		sel, id = content
		
		return_components = []
		for i in range(3):
			if assignto != None:
				return_components.append(assignto[i])
			else:
				return_components.append(func.get_scratch())
		
		if not func.get_vector_path(sel, id, return_components):
			for i in range(3):
				var = '_{0}_{1}'.format(id, i)
				func.register_objective(var)
				func.add_command('scoreboard players operation Global {0} = {1} {2}'.format(return_components[i], sel, var))
		
		return return_components
	
	elif type == 'VECTOR_BINOP_VECTOR' or type == 'VECTOR_BINOP_SCALAR':
		lhs, op, rhs = content
		
		return_components = []
		
		left_component_vars = calc_vector_math(func, lhs, assignto)
		if left_component_vars == None:
			return None
			
		for i in range(3):
			if func.is_scratch(left_component_vars[i]):
				return_components.append(left_component_vars[i])
			elif assignto != None and left_component_vars[i] == assignto[i]:
				return_components.append(left_component_vars[i])
			else:
				newId = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, left_component_vars[i]))
				return_components.append(newId)
		
		if type == 'VECTOR_BINOP_VECTOR':
			right_component_vars = calc_vector_math(func, rhs)
			if right_component_vars == None:
				return None
				
			for i in range(3):
				func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], op, right_component_vars[i]))
				func.free_scratch(right_component_vars[i])
		
		if type == 'VECTOR_BINOP_SCALAR':
			right_var = calc_math(func, rhs)
			if right_var == None:
				return None
			
			for i in range(3):
				func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], op, right_var))
				
			func.free_scratch(right_var)
		
		return return_components	
	
	if type == 'VECTOR_HERE':
		scale = content
		if scale == None:
			scale = func.scale
		
		func.register_objective('_age')
		func.add_command('scoreboard players add @e _age 1')
		func.add_command('summon area_effect_cloud')
		func.add_command('scoreboard players add @e _age 1')
		
		return_components = []
		for i in range(3):
			if assignto != None:
				return_components.append(assignto[i])
			else:
				return_components.append(func.get_scratch())
		
			func.add_command('execute store result score Global {0} run data get entity @e[_age==1,limit=1] Pos[{1}] {2}'.format(return_components[i], i, scale))
		
		func.add_command('/kill @e[_age==1]')
		
		return return_components

def calc_math(func, expr, assignto = None):
	etype = expr[0]
	
	if etype == 'SELVAR':
		func.register_objective(expr[2])
		
		func.get_path(expr[1], expr[2])
		
		if assignto != None:
			newId = assignto
		elif expr[1] != 'Global':
			newId = func.get_scratch()
		else:
			newId = expr[2]
		
		if expr[1] != 'Global' or newId != expr[2]:
			func.add_command("scoreboard players operation Global {0} = {1} {2}".format(newId, expr[1], expr[2]))
		
		return newId
		
	if etype == 'BINOP':
		type = expr[1]
		
		if len(type) == 1 and type in "+-*/%":
			if type in "+*" and (expr[2][0] == 'NUM' or expr[2][0] == 'SCALE') and expr[3][0] != 'NUM' and expr[3][0] != 'SCALE':
				left = expr[3]
				right = expr[2]
			else:
				left = expr[2]
				right = expr[3]
		
			id1 = calc_math(func, left, assignto=assignto)
			if id1 == None:
				print "Unable to compile LHS of binop {0}".format(type)
				return None
			
			id1 = get_modifiable_id(func, id1, assignto)
				
			if right[0] == 'NUM' or right[0] == 'SCALE':
				if right[0] == 'NUM':
					val = func.apply_replacements(right[1])
					operand2 = int(val)
						
				elif right[0] == 'SCALE':
					operand2 = int(func.scale)
					
				if type == '+':
					if operand2 >= 0:
						func.add_command('scoreboard players add Global {0} {1}'.format(id1, operand2))
					else:
						func.add_command('scoreboard players remove Global {0} {1}'.format(id1, -operand2))
				elif type == '-':
					if operand2 >= 0:
						func.add_command('scoreboard players remove Global {0} {1}'.format(id1, operand2))
					else:
						func.add_command('scoreboard players add Global {0} {1}'.format(id1, -operand2))
				else:
					id2 = func.add_constant(operand2)
					func.add_command('scoreboard players operation Global {0} {1}= {2} Constant'.format(id1, type, id2))
			elif right[0] == 'SELVAR':
				func.register_objective(right[2])
		
				func.get_path(right[1], right[2])
					
				func.add_command('scoreboard players operation Global {} {}= {} {}'.format(id1, type, right[1], right[2]))
				
				return id1
				
			else:
				id2 = calc_math(func, right)
				if id2 == None:
					print "Unable to compile RHS of binop {0}".format(type)
					return None
				
				func.add_operation('Global', id1, type+'=', id2)
				if func.is_scratch(id2):
					func.free_scratch(id2)
			
			return id1
			
		if type == "^":
			target = calc_math(func, expr[2], assignto=assignto)
			
			if target == None:
				print 'Unable to compile exponent for ^'
				return None
			
			power = int(expr[3])
			
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
			
		print "Binary operation '{0}' isn't implemented".format(type)
		return None
		
	if etype == 'DOT':
		lhs = calc_vector_math(func, expr[1])
		rhs = calc_vector_math(func, expr[2])
		
		prods = []
		for i in range(3):
			prod = lhs[i]
			if not func.is_scratch(prod):
				prod = func.get_scratch()
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(prod, lhs[i]))
			func.add_command('scoreboard players operation Global {0} *= Global {1}'.format(prod, rhs[i]))
			
			prods.append(prod)
			
		func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[1]))
		func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[2]))
		
		for i in range(3):
			for vec in [lhs, rhs, prod]:
				if vec[i] != prods[0]:
					func.free_scratch(vec[i])
		
		return prods[0]
		
	if etype == 'NUM' or etype == 'SCALE': 
		if assignto != None:
			id = assignto
		else:
			id = func.get_scratch()
			
		if etype == 'NUM':
			val = expr[1]
		elif etype == 'SCALE':
			val = func.scale
			
		func.add_command("scoreboard players set Global {0} {1}".format(id, val))
		
		return id
		
	if etype == 'ARRAYCONST':
		array_var = get_arrayconst_var(func, expr[1], expr[2])
		
		return array_var
		
	if etype == 'ARRAYEXPR':
		array = expr[1]
		
		if array not in func.arrays:
			print('Tried to use undefined array "{}"'.format(array))
			return None
			
		index_var = '{}Idx'.format(array)
		id = calc_math(func, expr[2], assignto=index_var)
		if id == None:
			return None
		
		if id != index_var:
			func.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
			
		func.add_command('function {}:array_{}_get'.format(func.namespace, array.lower()))
		
		func.free_scratch(id)
		
		return '{}Val'.format(array)
		
	if etype == 'UNARY':
		type = expr[1]
		if type == "-":
			id = calc_math(func, expr[2], assignto)
			
			if id == None:
				return None
			
			id = get_modifiable_id(func, id, assignto)

			func.add_constant(-1)
			func.add_command("scoreboard players operation Global {0} *= minus Constant".format(id))
			
			return id
		
		
		print "Unary operation '{0}' isn't implemented.".format(type)
		return None
		
	if etype == 'FUNC':
		call = expr[1]
		efunc = call.dest
		args = call.args
		
		if efunc == 'sqrt':
			if len(args) <> 1:
				print "sqrt takes exactly 1 argument, received: {0}".format(args)
				return None
			
			id = calc_math(func, args[0])
			if id == None:
				print 'Unable to compile argument for sqrt'
				return None
			
			guess = calc_math(func, scriptparse.parse("20")[1])
			
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
			
			id = calc_math(func, args[0])
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
			call.compile(func)
			
			return "ReturnValue"
		
		return None
			
	print "Unable to interpret math block."
	
	return None


def get_if_chain(func, conditions, iftype='if'):
	test = ''
	for type, val in conditions:
		if type == 'selector':
			test += '{0} entity {1} '.format(iftype, val)
		elif type == 'score':
			var, op, (rtype, rval) = val
			
			lselector, lvar = get_variable(func, var, initialize = True)
			
			func.register_objective(lvar)
			func.get_path(lselector, lvar)
			
			if rtype == 'num':
				rval = func.apply_replacements(rval)
				if op == '>':						
					test += '{3} score {0} {1} matches {2}.. '.format(lselector, lvar, str(int(rval)+1), iftype)
				if op == '>=':						
					test += '{3} score {0} {1} matches {2}.. '.format(lselector, lvar, rval, iftype)
				if op == '<':						
					test += '{3} score {0} {1} matches ..{2} '.format(lselector, lvar, str(int(rval)-1), iftype)
				if op == '<=':						
					test += '{3} score {0} {1} matches ..{2} '.format(lselector, lvar, rval, iftype)
				if op == '=':						
					test += '{3} score {0} {1} matches {2}..{2} '.format(lselector, lvar, rval, iftype)
			elif rtype == 'score':
				rselector, rvar = get_variable(func, rval, initialize = True)
				
				func.register_objective(rvar)
				func.get_path(rselector, rvar)
				test += '{0} score {1} {2} {3} {4} {5} '.format(iftype, lselector, lvar, op, rselector, rvar)
				
		elif type == 'pointer':
			var, rselector = val
			
			lselector, id = get_variable(func, var, initialize = True)
			
			func.register_objective(id)
			test += '{0} score {1} {2} = {3} _id '.format(iftype, lselector, id, rselector)
			
		elif type == 'vector_equality':
			if iftype == 'unless':
				print('Vector equality may not  be used with "unless"')
				return None
			
			(type1, var1), (type2, var2) = val
			
			for i in range(3):
				if type1 == 'VAR_ID':
					sel1 = 'Global'
					sco1 = '_{}_{}'.format(var1, i)
				elif type1 == 'SEL_VAR_ID':
					sel1, selvar1 = var1
					sco1 = '_{}_{}'.format(selvar1, i)
				elif type1 == 'VAR_COMPONENTS':
					sel1, sco1 = var1[i]
					
				if type2 == 'VAR_ID':
					sel2 = 'Global'
					sco2 = '_{}_{}'.format(var2, i)
				elif type2 == 'SEL_VAR_ID':
					sel2, selvar2 = var2
					sco2 = '_{}_{}'.format(selvar2, i)
				elif type2 == 'VAR_COMPONENTS':
					sel2, sco2 = var1[i]
				test += 'if score {} {} = {} {} '.format(sel1, sco1, sel2, sco2)
				
		elif type == 'block':
			relcoords, block = val
			if block in func.block_tags:
				block = '#{0}:{1}'.format(func.namespace, block)
			else:
				block = 'minecraft:{0}'.format(block)
			test += '{0} block {1} {2} '.format(iftype, ' '.join(relcoords), block)
		else:
			print('Unknown "if" type: {0}'.format(type))
			return None
	
	return test


def get_execute_command(exec_items, func, exec_func):	
	cmd = 'execute '
	as_count = 0
	for type, _ in exec_items:
		if type[:2] == 'As':
			as_count += 1
			
			if as_count >= 2:
				print('Execute chain may only contain a single "as" clause in block at line {0}'.format(get_line(line)))
				return None
	
	at_vector_count = 0
	
	for type, val in exec_items:
		if type == 'If':
			cmd += get_if_chain(func, val)
		if type == 'Unless':
			cmd += get_if_chain(func, val, 'unless')
		elif type == 'As':
			cmd += 'as {0} '.format(val)
			exec_func.update_self_selector(val)
		elif type == 'AsId':
			var, attype = val
			
			selector, id = get_variable(func, var, initialize = True)
			
			func.register_objective('_id')
			func.register_objective(id)
			
			func.add_command('scoreboard players operation Global _id = {0} {1}'.format(selector, id))
								
			cmd += 'as @e if score @s _id = Global _id '.format(selector, id)
			
			if attype != None:
				exec_func.update_self_selector('@' + attype)
			else:
				exec_func.update_self_selector('@s')
		elif type == 'AsCreate':
			if len(exec_items) > 1:
				print('"as create" must be its own block at line {0}'.format(get_line(line)))
				return None
			create_operation = val
				
			func.register_objective('_age')
			func.add_command('scoreboard players add @e _age 1')
			
			create_operation.compile(func)
				
			func.add_command('scoreboard players add @e _age 1')
			cmd += 'as @e[_age==1] '
			
			exec_func.update_self_selector('@'+create_operation.atid)
		elif type == 'Rotated':
			cmd += 'rotated as {0} '.format(val)
		elif type == 'FacingCoords':
			cmd += 'facing {0} '.format(' '.join(val))
		elif type == 'FacingEntity':
			cmd += 'facing entity {0} feet '.format(val)
		elif type == 'Align':
			cmd += 'align {0} '.format(val)
		elif type == 'At':
			selector, relcoords = val
			if selector != None:
				cmd += 'at {0} '.format(selector)
			if relcoords != None:
				cmd += 'positioned {0} '.format(' '.join(relcoords))
		elif type == 'AtVector':
			at_vector_count += 1
			if at_vector_count >= 2:
				print('Tried to execute at multiple vector locations.')
				return None
				
			scale, expr = val
			if scale == None:
				scale = func.scale

			vec_vals = calc_vector_math(func, expr)
			func.add_command('scoreboard players add @e _age 1')
			func.add_command('summon area_effect_cloud')
			func.add_command('scoreboard players add @e _age 1')
			for i in range(3):
				func.add_command('execute store result entity @e[_age==1,limit=1] Pos[{0}] double {1} run scoreboard players get Global {2}'.format(i, 1/float(scale), vec_vals[i]))
			cmd += 'at @e[_age == 1] '
			exec_func.add_command('/kill @e[_age == 1]')
		elif type == 'In':
			dimension = val
			cmd += 'in {} '.format(dimension)
			
	return cmd
	

class mcfunction(object):
	def __init__(self, environment, callable = False, params = []):
		self.commands = []
		self.environment = environment
		self.params = params
		self.callable = callable
		self.environment_stack = []
		
		for param in params:
			self.register_local(param)
		
	def add_operation(self, selector, id1, operation, id2):
		selector = self.environment.apply(selector)
		
		self.add_command("scoreboard players operation {0} {1} {2} {0} {3}".format(selector, id1, operation, id2))
			
		if self.environment.scratch.is_scratch(id2):
			self.environment.scratch.free_scratch(id2)
		
	def add_command(self, command):
		self.insert_command(command, len(self.commands))
	
	def insert_command(self, command, index):
		if len(command) == 0:
			return
		
		if command[0] != '#':
			if command[0] == '/':
				command = command[1:]
		
			command = self.environment.apply(command)
			
		self.commands.insert(index, command)
		
	def get_utf8_text(self):
		return "\n".join([(cmd if cmd[0] != '/' else cmd[1:]) for cmd in self.commands]).encode('utf-8')
		
	def defined_objectives(self):
		existing = {}
		defineStr = "scoreboard objectives add " 
		for cmd in self.commands:
			if cmd[0] == '/':
				cmd = cmd[1:]
			if cmd[:len(defineStr)] == defineStr:
				existing[cmd[len(defineStr):].split(' ')[0]] = True
				
		return existing
		
	def register_local(self, id):
		self.environment.register_local(id)
			
	def finalize(self):
		comments = []
		while len(self.commands) > 0 and len(self.commands[0]) >= 2 and self.commands[0][0:2] == '##':
			comments.append(self.commands[0])
			del self.commands[0]
	
		if self.callable:
			for v in self.environment.scratch.get_allocated_variables():
				self.register_local(v)
	
			for p in range(len(self.params)):
				self.insert_command('scoreboard players operation Global {0} = Global Param{1}'.format(self.params[p], p), 0)
				self.environment.global_context.register_objective("Param{0}".format(p))
			
		self.commands = comments + self.commands
		
	def single_command(self):
		ret = None
		count = 0
		for cmd in self.commands:
			if not cmd.startswith('#') and len(cmd) > 0:
				ret = cmd
				count += 1
			
			if count >= 2:
				return None
				
		return ret
			
	def check_single_entity(self, selector):
		if selector[0] != '@':
			return True
			
		parsed = selector_definition(selector, self.environment)
		return parsed.single_entity()
			
	def get_path(self, selector, var):
		if selector[0] != '@':
			return
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.environment.selectors:
			sel_def = self.environment.selectors[id]
		elif id == 's' and self.environment.self_selector != None:
			sel_def = self.environment.self_selector
		else:
			return
			
		if var in sel_def.paths:
			path, data_type, scale = sel_def.paths[var]
			if scale == None:
				scale = self.environment.global_context.scale
			
			if not self.check_single_entity(selector):
				raise Exception('Tried to get data "{0}" from selector "{1}" which is not limited to a single entity.'.format(var, selector))
				
			self.add_command('execute store result score {0} {1} run data get entity {0} {2} {3}'.format(selector, var, path, scale))
				
	def set_path(self, selector, var):
		if selector[0] != '@':
			return
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.environment.selectors:
			sel_def = self.environment.selectors[id]
		elif id == 's' and self.environment.self_selector != None:
			sel_def = self.environment.self_selector
		else:
			return
			
		if var in sel_def.paths:
			path, data_type, scale = sel_def.paths[var]
			if scale == None:
				scale = self.environment.global_context.scale

			if not self.check_single_entity(selector):
				raise Exception('Tried to set data "{0}" for selector "{1}" which is not limited to a single entity.'.format(var, selector))
				
			self.add_command('execute store result entity {0} {2} {3} {4} run scoreboard players get {0} {1}'.format(selector, var, path, data_type, 1/float(scale)))

	def get_vector_path(self, selector, var, assignto):
		if selector[0] != '@':
			return
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.environment.selectors:
			sel_def = self.environment.selectors[id]
		elif id == 's' and self.environment.self_selector != None:
			sel_def = self.environment.self_selector
		else:
			return False
			
		if var in sel_def.vector_paths:
			path, data_type, scale = sel_def.vector_paths[var]
			if scale == None:
				scale = self.environment.global_context.scale

			if not self.check_single_entity(selector):
				raise Exception('Tried to get vector data "{0}" from selector "{1}" which is not limited to a single entity.'.format(var, selector))
				
			for i in range(3):
				self.add_command('execute store result score Global {0} run data get entity {1} {2}[{3}] {4}'.format(assignto[i], selector, path, i, scale))
			
			return True
		else:
			return False
			
	def set_vector_path(self, selector, var, values):
		if selector[0] != '@':
			return False
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.environment.selectors:
			sel_def = self.environment.selectors[id]
		elif id == 's' and self.environment.self_selector != None:
			sel_def = self.environment.self_selector
		else:
			return False
			
		if var in sel_def.vector_paths:
			path, data_type, scale = sel_def.vector_paths[var]
			if scale == None:
				scale = self.environment.global_context.scale

			if not self.check_single_entity(selector):
				raise Exception('Tried to set vector data "{0}" for selector "{1}" which is not limited to a single entity.'.format(var, selector))
				
			for i in range(3):
				self.add_command('execute store result entity {0} {1}[{2}] {3} {4} run scoreboard players get Global {5}'.format(selector, path, i, data_type, 1/float(scale), values[i]))
			
			return True
		else:
			return False
			
	def register_objective(self, objective):
		self.environment.register_objective(objective)
		
	def register_array(self, name, from_val, to_val):
		self.environment.register_array(name, from_val, to_val)
		
	def apply_replacements(self, text):
		return self.environment.apply_replacements(text)
		
	def register_block_tag(self, name, blocks):
		self.environment.register_block_tag(name, blocks)
		
	def get_scale(self):
		return self.environment.scale
		
	def set_scale(self, scale):
		self.environment.scale = scale
		
	scale = property(get_scale, set_scale)
	
	@property
	def arrays(self):
		return self.environment.arrays
		
	@property
	def block_tags(self):
		return self.environment.block_tags

	@property
	def namespace(self):
		return self.environment.namespace
		
	@property
	def macros(self):
		return self.environment.macros
		
	@property
	def template_functions(self):
		return self.environment.template_functions
		
	@property
	def functions(self):
		return self.environment.functions
		
	@property
	def selectors(self):
		return self.environment.selectors
	
	def get_scratch(self):
		return self.environment.get_scratch()
		
	def get_scratch_vector(self):
		return self.environment.get_scratch_vector()
		
	def is_scratch(self, var):
		return self.environment.is_scratch(var)
	
	def free_scratch(self, id):
		self.environment.free_scratch(id)
		
	def get_temp_var(self):
		return self.environment.get_temp_var()
		
	def free_temp_var(self):
		self.environment.free_temp_var()
		
	def apply_environment(self, text):
		return self.environment.apply(text)
		
	def add_constant(self, val):
		return self.environment.add_constant(val)
		
	def allocate_rand(self, val):
		self.environment.allocate_rand(val)
		
	def get_friendly_name(self):
		return self.environment.get_friendly_name()
		
	def get_random_objective(self):
		return self.environment.get_random_objective()
		
	def register_function(self, name, func):
		self.environment.register_function(name, func)
		
	def get_unique_id(self):
		return self.environment.get_unique_id()
		
	def update_self_selector(self, selector):
		self.environment.update_self_selector(selector)
		
	def get_python_env(self):
		return self.environment.get_python_env()
		
	def clone_environment(self):
		return self.environment.clone()
		
	# Combines a selector with an existing selector definition in the environment
	def get_combined_selector(self, selector):
		return selector_definition(selector, self.environment)
		
	def set_dollarid(self, id, val):
		self.environment.set_dollarid(id, val)
		
	def set_atid(self, id, fullselector):
		return self.environment.set_atid(id, fullselector)
		
	def push_environment(self, new_env):
		self.environment_stack.append(self.environment)
		self.environment = new_env
		
	def pop_environment(self):
		self.environment = self.environment_stack.pop()
		
	def run_create(self, atid, relcoords):
		if atid not in self.selectors:
			print('Unable to create unknown entity: @{0}'.format(atid))
			return False
		
		selector = self.selectors[atid]
		
		entity_type = selector.get_type()
		
		if entity_type == None:
			print('Unable to create @{0}, no entity type is defined.'.format(atid))
			return False
			
		if selector.tag == None:
			self.add_command('summon {0} {1}'.format(entity_type, ' '.join(relcoords)))
		else:
			self.add_command('summon {0} {1} {2}'.format(entity_type, ' '.join(relcoords), selector.tag))
			
		return True
		
	# Creates an empty function with a copy of the current environment
	def create_child_function(self):
		return mcfunction(self.clone_environment())
		

	def compile_blocks(self, lines):
		for block in lines:
			try:
				block.compile(self)
			except Exception as e:
				print('Exception while compiling block at line {}'.format(block.line))
				print(e)
				raise
		
		return True