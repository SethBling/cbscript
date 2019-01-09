import scriptparse
from scriptparse import get_line
import global_context
import mcworld
from environment import environment
from mcfunction import mcfunction
from selector_definition import selector_definition
import tellraw
import traceback
import math
import collections

def compile_section(section, environment):
	type, name, template_params, params, lines = section

	if type == 'function':
		f = mcfunction(environment.clone(new_function_name = name), True, params)
	else:
		f = mcfunction(environment.clone(new_function_name = name))
		
	environment.register_function(name, f)

	if type == 'clock':
		environment.register_clock(name)
		
	if not compile_block(f, lines):
		return False
			
	return True

def compile_block(func, lines):
	for line in lines:
		try:
			if not compile(func, line):
				print 'Unable to compile block at line {0}'.format(get_line(line))
				return False
		except Exception as e:
			print('Exception while compiling block at line {}'.format(get_line(line)))
			raise
	
	return True
	
def compile(func, line):
	(type, content) = line
	if type == 'Comment':
		func.add_command(content)
	
	elif type == 'Command':
		func.add_command(content)
		
	elif type == 'Move':
		selector, coords = content
		if selector == '@s':
			cmd = 'execute at @s run tp @s {0}'.format(' '.join(coords))
		else:
			cmd = 'execute as {0} at @s run tp @s {1}'.format(selector, ' '.join(coords))
		
		func.add_command(cmd)
		
	elif type == 'PythonAssignment':
		id, python = content
		
		try:
			func.set_dollarid(id, eval(python, globals(), func.get_python_env()))
		except Exception as e:
			print('Could not evaluate "{0}" at line {1}'.format(python, get_line(line)))
			print(e)
			return False
		
	elif type == 'For':
		identifier, setpython, sub = content
		
		try:
			set = eval(setpython, globals(), func.get_python_env())
		except:
			print('Could not evaluate "{0}" in "for" block at line {1}'.format(setpython, get_line(line)))
			return False
		
		try:
			iter(set)
		except:
			print '"{0}" in "for" block at line {1} is not an iterable set.'.format(setpython, get_line(line))
			return False

		for v in set:
			func.set_dollarid(identifier, v)
			if not compile_block(func, sub):
				return False
		
	elif type == 'SelectorAssignment':
		id, fullselector = content
		
		func.set_atid(id, fullselector)
		
	elif type == 'SelectorDefinition':
		id, fullselector, items = content
		
		selector = func.set_atid(id, fullselector)
		
		for type, val in items:
			if type == 'Tag':
				selector.tag = val
			elif type == 'Path':
				path_id, path, data_type, scale = val
				if scale == None:
					scale = func.scale
				selector.paths[path_id] = (path, data_type, scale)
			elif type == 'VectorPath':
				vector_id, path, data_type, scale = val
				if scale == None:
					scale = func.scale
				selector.vector_paths[vector_id] = (path, data_type, scale)
			elif type == 'Method':
				sub_env = func.clone_environment()
				sub_env.update_self_selector('@'+id)
				if not compile_section(val, sub_env):
					return False
			else:
				print('Unknown selector item type "{0}" in selector definition at line {1}'.format(type, get_line(line)))
				return False
				
	elif type == 'BlockTag':
		name, blocks = content
		func.register_block_tag(name, blocks)
		
	elif type == 'ArrayDefinition':
		name, from_val, to_val = content
		
		from_val = int(func.apply_replacements(from_val))
		to_val = int(func.apply_replacements(to_val))

		vals = list(range(from_val, to_val))
		
		for i in vals:
			func.register_objective('{}{}'.format(name, i))
		
		valvar = '{}Val'.format(name)
		func.register_objective(valvar)
		
		indexvar = '{}Idx'.format(name)
		func.register_objective(indexvar)
		
		line = get_line(line)

		get_func = mcfunction(func.clone_environment())
		get_func_name = 'array_{}_get'.format(name.lower())
		func.register_function(get_func_name, get_func)
		cases = [(i, i, [('Command', '/scoreboard players operation Global {} = Global {}{}'.format(valvar, name, i))], line, None) for i in vals]
		if not switch_cases(get_func, indexvar, cases, 'arrayget', 'arraygetidx'):
			return False
		
		set_func = mcfunction(func.clone_environment())
		set_func_name = 'array_{}_set'.format(name.lower())
		func.register_function(set_func_name, set_func)
		cases = [(i, i, [('Command', '/scoreboard players operation Global {}{} = Global {}'.format(name, i, valvar))], line, None) for i in vals]
		if not switch_cases(set_func, indexvar, cases, 'arrayset', 'arraysetidx'):
			return False
			
		func.register_array(name, from_val, to_val)
		
	elif type == 'Create':
		atid, relcoords = content
		
		if not func.run_create(atid, relcoords):
			print('Error creating entity at line {0}'.format(get_line(line)))
			return False
		
	elif type == 'ArrayAssignment':
		name, (idxtype, idxval), expr = content
		
		if name not in func.arrays:
			print('Tried to assign to undefined array "{}"'.format(name))
			return False
		
		if idxtype == 'Const':
			array_var = get_arrayconst_var(func, name, idxval)
			
			id = calc_math(func, expr, assignto=array_var)
			
			if id == None:
				print('Unable to compute value for array assignment at line {}'.format(get_line(line)))
				return False
				
			if id != array_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(array_var, id))
				
			func.free_scratch(id)
		
		elif idxtype == 'Expr':
			val_var = '{}Val'.format(name)
			id1 = calc_math(func, expr, assignto=val_var)
			
			if id1 == None:
				print('Unable to compute value for array assignment at line {}'.format(get_line(line)))
				return False
			
			idx_var = '{}Idx'.format(name)
			
			id2 = calc_math(func, idxval, assignto=idx_var)
			if id2 == None:
				print('Unable to calculate array index at line {}'.format(get_line(line)))
				return False
				
			if id1 != val_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(val_var, id1))
			
			if id2 != idx_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(idx_var, id2))
				
			func.add_command('function {}:array_{}_set'.format(func.namespace, name.lower()))
			
			func.free_scratch(id1)
			func.free_scratch(id2)
	
	elif type == 'ScoreboardAssignment':
		var, op, expr = content
		
		if op in ['+=', '-=', '*=', '/=', '%=']:
			modify = True
		else:
			modify = False
		
		(raw_selector, objective) = get_variable(func, var, initialize = modify)
		
		selector = func.apply_environment(raw_selector)
		
		if op in ['+=', '-=', '='] and expr[0] == 'NUM' or expr[0] == 'SCALE':
			if expr[0] == 'NUM':
				operand = func.apply_environment(expr[1])
			else:
				operand = func.scale
			
			if not isNumber(operand):
				print "Unable to apply {0} to {1} at line {2}.".format(op, operand, get_line(line))
				return False
				
			operand = int(operand)
			
			if op == '+=':
				opword = 'add'
			elif op == '-=':
				opword = 'remove'
			elif op == '=':
				opword = 'set'
			else:
				print('Unknown selector arithmetic operation: "{0}" at line {1}'.format(op, get_line(line)))
				return False
				
			func.add_command('/scoreboard players {0} {1} {2} {3}'.format(opword, selector, objective, operand))
			
		elif expr[0] == 'NUM' or expr[0] == 'SCALE':
			if expr[0] == 'NUM':
				operand = func.apply_environment(expr[1])
			elif expr[0] == 'SCALE':
				operand = func.scale
			
			if not isNumber(operand):
				print "Unable to apply {0} to {1} at line {2}.".format(op, operand, get_line(line))
				return False
				
			operand = int(operand)
		
			id2 = func.add_constant(operand)
			command = "/scoreboard players operation {0} {1} {2} {3} {4}".format(selector, objective, op, id2, "Constant")
			
			func.add_command(command)
			
			set_variable(func, var)
			
		elif op == '=' and expr[0] == 'Selector':
			target = expr[1]
			
			if not func.check_single_entity(target):
				print('Selector "{0}" not limited to a single entity at line {1}'.format(target, get_line(line)))
				return False
		
			func.register_objective('_unique')
			func.register_objective('_id')
			func.add_command('scoreboard players add Global _unique 1')
			func.add_command('execute unless score {0} _id matches 0.. run scoreboard players operation {0} _id = Global _unique'.format(target))
			func.add_command('scoreboard players operation {0} {1} = {2} _id'.format(selector, objective, target))
			
		elif op == '=' and expr[0] == 'Create':
			atid, relcoords = expr[1]
			
			func.register_objective('_age')
			func.register_objective('_unique')
			func.register_objective('_id')
			
			func.add_command('scoreboard players add @e _age 1')
							
			if not func.run_create(atid, relcoords):
				print('Error creating entity at line {0}'.format(get_line(line)))
				return False
				
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
				print 'Unable to compile assignment operand for {0} {1} {2} at line {3}.'.format(selector, objective, op, get_line(line))
				return False
				
			if selector != 'Global' or result != objective or op != '=':
				func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(selector, objective, op, result))
				
			func.free_scratch(result)

		set_variable(func, var)
		
	elif type == 'VectorAssignment' or type == 'VectorAssignmentScalar':
		var, op, expr = content
		
		if not perform_vector_assignment(func, type, get_line(line), var, op, expr):
			return False

	elif type == 'Execute' or type == 'While':
		exec_items, sub = content
		
		if not func.perform_execute(type, get_line(line), exec_items, sub):
			return False
			
	elif type == 'ForSelector':
		id, selector, sub = content
		
		scratch_id = func.get_scratch()
		
		exec_func = mcfunction(func.clone_environment())
		
		combined_selector = func.get_combined_selector(selector)
		combined_selector.scores_min[scratch_id] = 1
		combined_selector.set_part('limit', '1')
		exec_func.selectors[id] = combined_selector
		exec_func.update_self_selector(selector)
		
		func.add_command('scoreboard players set {0} {1} 0'.format(selector, scratch_id))
		exec_func.add_command('scoreboard players set @s {0} 1'.format(scratch_id))
		if not compile_block(exec_func, sub):
			return False
		exec_func.add_command('scoreboard players set @s {0} 0'.format(scratch_id))
		
		func.free_scratch(scratch_id)
		
		unique = func.get_unique_id()
		exec_name = 'for{0:03}_ln{1}'.format(unique, get_line(line))
		func.register_function(exec_name, exec_func)
		
		func.add_command('execute as {0} run function {1}:{2}'.format(selector, func.namespace, exec_name))
			
	elif type == 'If':
		ifpython, sub, else_sub = content
		
		try:
			condition = eval(ifpython, globals(), func.get_python_env())
		except:
			print('Could not evaluate "{0}" in "if" block at line {1}'.format(ifpython, get_line(line)))
			return False
	
		if condition:
			if not compile_block(func, sub):
				return False

	elif type == 'ForIndex':
		var, fr, to, by, sub = content
		
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
		loop_func_name = 'for{0:03}_ln{1}'.format(unique, get_line(line))
		
		new_env = func.clone_environment()
		loop_func = mcfunction(new_env)
		func.register_function(loop_func_name, loop_func)	
		
		if not compile_block(loop_func, sub):
			return False
		
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

	elif type == 'Switch':
		expr, cases_raw = content
		
		result = calc_math(func, expr)
		if result == None:
			print('Unable to compute switch expression at line {}'.format(get_line(line)))
			return False

		cases = []
		for case in cases_raw:
			type, content = case
			line = get_line(case)
			if type == 'range':
				vmin, vmax, sub = content
				vmin = int(func.apply_replacements(vmin))
				vmax = int(func.apply_replacements(vmax))
				cases.append((vmin, vmax, sub, line, None))
			elif type == 'python':
				dollarid, python, sub = content
				try:
					vals = eval(python, globals(), func.get_python_env())
				except:
					print('Could not evaluate "{0}" at line {1}'.format(python, line))
					return False
				
				if not isinstance(vals, collections.Iterable):
					print('Python "{}" is not iterable at line {}'.format(python, line))
					return False

				for val in vals:
					try:
						ival = int(val)
					except:
						print('Value "{}" is not an integer at line {}'.format(val, line))
						return False
					cases.append((ival, ival, sub, line, dollarid))
			else:
				print('Unknown switch case type "{}"'.format(type))
				return False
		
		cases = sorted(cases, key=lambda case: case[0])
		
		# Check that none of the cases overlap
		prevmax = cases[0][0]-1
		for vmin, vmax, sub, line, dollarid in cases:
			if vmin > vmax:
				print('"case {}-{}" has invalid range at line {}'.format(vmin, vmax, line))
				return False
			if vmin <= prevmax:
				if vmin == vmax:
					rangestr = '{}'.format(vmin)
				else:
					rangestr = '{}-{}'.format(vmin, vmax)
				print('"case {}" overlaps another case at line {}'.format(rangestr, line))
				return False
			prevmax = vmax
			
		if not switch_cases(func, result, cases):
			return False
				
		func.free_scratch(result)
			
	elif type == 'Call':
		dest, params = content
		
		if not evaluate_params(func, params):
			return False
		
		func.add_command('function {0}:{1}'.format(func.namespace, dest))
	
	elif type == 'MethodCall':
		selector, dest, params = content
		
		if not evaluate_params(func, params):
			return False
		
		if selector == '@s':
			func.add_command('function {0}:{1}'.format(func.namespace, dest))
		else:
			func.add_command('execute as {0} run function {1}:{2}'.format(selector, func.namespace, dest))
		
	elif type == 'MacroCall':
		macro, args = content
		
		if macro not in func.macros:
			print('Line {1}: macro "{0}" does not exist'.format(macro, get_line(line)))
			return False
			
		params, sub = func.macros[macro]
			
		if len(args) != len(params):
			print('Tried to call Macro "{0}" with {1} arguments at line {3}, but it requires {2}'.format(macro, len(args), len(params), get_line(line)))
			return False
			
		new_env = func.clone_environment()
			
		for p in range(len(params)):
			if isNumber(args[p]):
				if args[p].isdigit() or args[p][0] == '-' and args[p][1:].isdigit():
					new_env.set_dollarid(params[p], int(args[p]))
				else:
					new_env.set_dollarid(params[p], float(args[p]))
			elif args[p].startswith('$'):
				new_env.copy_dollarid(params[p], args[p])
			else:
				print('Unknown macro parameter "{0}"'.format(args[p]))
				
		func.push_environment(new_env)
		if not compile_block(func, sub):
			return False
		func.pop_environment()
		
	elif type == 'TemplateFunctionCall':
		function, template_args, args = content
		
		if function not in func.template_functions:
			print('Tried to call non-existant template function "{}" at line {}'.format(function, get_line(line)))
			return False
		
		template_params, params, sub = func.template_functions[function]
		
		if len(template_args) != len(template_params):
			print('Tried to call template function "{}" with {} template arguments at line {}'.format(function, len(template_args), get_line(line)))
			return False
			
		if len(args) != len(params):
			print('Tried to call template function "{}" with {} function arguments at line {}'.format(function, len(args), get_line(line)))
			return False
		
		# Get textual function name
		func_name = function
		for template_arg in template_args:
			template_arg_val = func.apply_replacements(template_arg)
			func_name = func_name + '_{}'.format(template_arg_val)
		
		# Calculate function arguments
		for i in range(len(args)):
			id = calc_math(args[i])
			if id == None:
				print('Unable to compute argument "{}" for template function "{}" at line {}'.format(params[i], function, get_line(line)))
				return False
			func.add_command('scoreboard players operation Global Param{} = Global {}'.format(i, id))
			func.free_scratch(id)
		
		# Compile the function if it doens't exist yet
		if func_name not in func.functions:
			new_env = func.clone_environment()
			
			# Bind template paramters in the function's environment
			for p in range(len(template_args)):
				if isNumber(template_args[p]):
					if template_args[p].isdigit() or template_args[p][0] == '-' and template_args[p][1:].isdigit():
						new_env.set_dollarid(template_params[p], int(template_args[p]))
					else:
						new_env.set_dollarid(template_params[p], float(template_args[p]))
				elif template_args[p].startswith('$'):
					new_env.copy_dollarid(template_params[p], template_args[p])
				else:
					print('Unknown macro parameter "{0}"'.format(template_args[p]))
			
			# Compile the new function
			new_func = mcfunction(new_env, True, params)
			if not compile_block(new_func, sub):
				return False
			
			# Register the new function
			func.register_function(func_name, new_func)
			
		func.add_command('function {}:{}'.format(func.namespace, func_name))
	
	elif type == 'Tell':
		selector, unformatted = content
		
		text = tellraw.formatJsonText(func, unformatted)
		command = '/tellraw {0} {1}'.format(selector, text)
		func.add_command(command)
	elif type == 'Title':
		subtype, selector, times, unformatted = content
		
		if times != None:
			func.add_command('/title {} times {}'.format(selector, ' '.join(times)))
		
		text = tellraw.formatJsonText(func, unformatted)
		command = '/title {} {} {}'.format(selector, subtype, text)
		func.add_command(command)
	else:
		print('Unexpected code block type "{0}" at line {1}'.format(type, get_line(line)))
		return False
		
	return True
	
def switch_cases(func, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
	if len(cases) == 1:
		vmin, vmax, sub, line, dollarid = cases[0]
		if dollarid != None:
			func.set_dollarid(dollarid, vmin)
		if not compile_block(func, sub):
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
				if not compile_block(case_func, sub):
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

def perform_vector_assignment(func, type, line_num, var, op, expr):
	var_type, var_content = var
	
	if op == '=':
		modify = False
	else:
		modify = True
	
	if var_type == 'VAR_COMPONENTS':
		# Get and initialize the 3 variables
		components = var_content
		component_vars = []
		
		for i in range(3):
			sel, id = get_variable(func, components[i], initialize = modify)
			component_vars.append((sel, id))
	
	if op == '=':
		assignto = []
		if var_type == 'VAR_ID':
			for i in range(3):
				var_name = '_{0}_{1}'.format(var_content, i)
				assignto.append(var_name)
		elif var_type == 'SEL_VAR_ID':
			assignto = None
		elif var_type == 'VAR_COMPONENTS':
			for sel, id in component_vars:
				if sel == 'Global':
					assignto.append(id)
				else:
					assignto = None
					break
	else:
		assignto = None
	
	if type == 'VectorAssignment':
		component_val_vars = calc_vector_math(func, expr, assignto)
		if component_val_vars == None:
			print('Unable to compute vector assignment at line {0}'.format(line_num))
			return False
	elif type == 'VectorAssignmentScalar':
		val_var = calc_math(func, expr)			
		component_val_vars = [val_var for i in range(3)]

	if var_type == 'VAR_ID':
		for i in range(3):
			var_name = '_{0}_{1}'.format(var_content, i)
			if var_name != component_val_vars[i]:
				func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(var_name, op, component_val_vars[i]))
			func.register_objective(var_name)
			
	elif var_type == 'SEL_VAR_ID':
		sel, id = var_content

		if op != '=':
			temp_vars = func.get_scratch_vector()
			if func.get_vector_path(sel, id, temp_vars):
				for i in range(3):
					func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(temp_vars[i], op, component_val_vars[i]))
			
				component_val_vars = temp_vars
			else:
				for var in temp_vars:
					func.free_scratch(var)
			
		if not func.set_vector_path(sel, id, component_val_vars):
			for i in range(3):
				var = '_{0}_{1}'.format(id, i)
				func.register_objective(var)
				func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, var, op, component_val_vars[i]))

	elif var_type == 'VAR_COMPONENTS':
		components = var_content
	
		for i in range(3):
			sel, id = component_vars[i]
			var = components[i]
			
			if sel != 'Global' or id != component_val_vars[i]:
				func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, id, op, component_val_vars[i]))
				
			set_variable(func, var)
			
	else:
		print('Unknown vector variable type "{0}" at line {1}'.format(var_type, line_num))
		return False

	for i in range(3):
		func.free_scratch(component_val_vars[i])
		
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
			func.add_command("/scoreboard players operation Global {0} = {1} {2}".format(newId, expr[1], expr[2]))
		
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
			
		func.add_command("/scoreboard players set Global {0} {1}".format(id, val))
		
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
			func.add_command("/scoreboard players operation Global {0} *= minus Constant".format(id))
			
			return id
		
		
		print "Unary operation '{0}' isn't implemented.".format(type)
		return None
		
	if etype == 'FUNC':
		efunc = expr[1]
		args = expr[2]
		
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
				func.add_command("/scoreboard players add Global {0} {1}".format(id, min))
			if min < 0:
				func.add_command("/scoreboard players remove Global {0} {1}".format(id, -min))
				
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
			func.add_command("/scoreboard players operation Global {0} %= {1} Constant".format(modId, c180))
			
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
			if not evaluate_params(func, args):
				return False
			
			func.add_command('/function {0}:{1}'.format(func.namespace, efunc))
			
			return "ReturnValue"
		
		return None
			
	print "Unable to interpret math block."
	
	return None

class cbscript(object):
	def __init__(self, source_file):
		self.source_file = source_file
		self.namespace = self.source_file.get_base_name().split('.')[0].lower()
		self.modified = self.source_file.get_last_modified()
	
	def check_for_update(self):
		last_modified = self.source_file.get_last_modified()
		
		if last_modified > self.modified:
			self.modified = last_modified
			self.try_to_compile()
	
	def try_to_compile(self):
		try:
			print('Compiling {0}...'.format(self.namespace))
			success = self.compile_all()
			if success:
				print "Script successfully applied."
			else:
				print "Script had compile error(s).\a"
		except SyntaxError as e:
			print(str(e) + '\a')
		except Exception as e:
			print "Compiler encountered unexpected error during compilation.\a"
			print type(e)
			print e.args
			print e
			traceback.print_exc()
		
	def compile_all(self):
		text = self.source_file.get_text()
	
		result = scriptparse.parse(text + "\n")
		
		if result == None:
			print('Unable to parse script.')
			return False
		
		type, parsed = result
		
		if type <> 'program':
			print('Script does not contain a full program.')
			return False
			
		self.global_context = global_context.global_context(self.namespace)
		global_environment = environment(self.global_context)
		global_func = mcfunction(global_environment)
		
		self.global_context.scale = parsed['scale']

		for assignment in parsed["assignments"]:
			if not compile(global_func, assignment):
				print "Error compiling assignment at line {0}".format(get_line(assignment))
				return False

		for section in parsed['sections']:
			type, id, template_params, params, sub = section
			if type == 'macro':
				self.global_context.macros[id] = (params, sub)
			elif type == 'template_function':
				self.global_context.template_functions[id] = (template_params, params, sub)
				
		for section in parsed["sections"]:
			if section[0] == 'macro' or section[0] == 'template_function':
				continue
			if not compile_section(section, global_environment):
				return False
		
		self.post_processing()
			
		world = mcworld.mcworld(parsed["dir"], self.namespace)

		world.write_functions(self.global_context.functions)
		world.write_tags(self.global_context.clocks, self.global_context.block_tags)
		world.write_mcmeta(parsed['desc'])
		world.write_zip()
			
		return True
		
	def post_processing(self):
		self.global_context.finalize_functions()
		self.add_scratch_objectives()
		self.add_temp_objectives()
		self.add_constants()
		self.add_random_generation()
		self.add_trigger_objectives()
		self.add_registered_objectives()
		
	def add_scratch_objectives(self):
		f = self.global_context.get_reset_function()
		
		for prefix in self.global_context.scratch:			
			for i in xrange(self.global_context.scratch[prefix]):
				f.insert_command('/scoreboard objectives add {0}_scratch{1} dummy'.format(prefix, i), 0)
	
	
	def add_temp_objectives(self):
		f = self.global_context.get_reset_function()
		
		for t in xrange(self.global_context.temp):
			f.insert_command('/scoreboard objectives add temp{0} dummy'.format(str(t)), 0)
	
	def add_constants(self):
		self.global_context.add_constant_definitions()
	
	def add_random_generation(self):
		f = self.global_context.get_reset_function()
		
		if self.global_context.rand > 0:
			objective = self.global_context.get_random_objective()
			f.add_command('/kill @e[type=armor_stand,name=RandBasis,scores={{{0}=0..}}]'.format(objective))
			f.add_command("/scoreboard objectives add {0} dummy".format(objective))
			for i in xrange(self.global_context.rand):
				f.add_command('/summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}')
				f.add_command('/scoreboard players add @e[type=armor_stand,name=RandBasis] {0} 1'.format(objective))
			f.add_command('/scoreboard players remove @e[type=armor_stand,name=RandBasis] {0} 1'.format(objective))	
			
	def add_trigger_objectives(self):
		None
	
	def add_registered_objectives(self):
		reset = self.global_context.get_reset_function()
		
		defined = reset.defined_objectives()
		
		for objective in self.global_context.objectives.keys():
			if objective not in defined:
				reset.insert_command("/scoreboard objectives add {0} dummy".format(objective), 0)