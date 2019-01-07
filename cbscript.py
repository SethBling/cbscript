import scriptparse
from scriptparse import get_line
import global_context
import mcworld
from environment import environment
from mcfunction import mcfunction
from selector_definition import selector_definition
import tellraw
import time
import os
import traceback
import math
import collections

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

		
class cbscript(object):
	def __init__(self, filename):
		self.macros = {}
		self.template_functions = {}
		self.filename = filename
		self.namespace = os.path.basename(self.filename).split('.')[0].lower()
		self.modified = self.get_last_modified()
		self.try_to_compile()
	
	def get_last_modified(self):
		return time.ctime(os.path.getmtime(self.filename))
		
	def check_for_update(self):
		last_modified = self.get_last_modified()
		
		if last_modified > self.modified:
			self.modified = last_modified
			self.try_to_compile()
	
	def get_friendly_name(self):
		name = "CB" + self.namespace[:14]
		name = name.replace(' ', '_')
		name = name.replace('.', '_')
		name = name.replace(',', '_')
		name = name.replace(':', '_')
		name = name.replace('{', '_')
		name = name.replace('}', '_')
		name = name.replace('=', '_')
		
		return name
	
	def get_random_objective(self):
		return "RV" + self.get_friendly_name()[2:]
		
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
		text = ""
		while len(text) == 0:
			with open(self.filename, 'r') as content_file:
				text = content_file.read()
			
			time.sleep(0.1)
		
		result = scriptparse.parse(text + "\n")
		
		if result == None:
			print('Unable to parse script.')
			return False
		
		type, parsed = result
		
		if type <> 'program':
			print('Script does not contain a full program.')
			return False
			
		self.global_context = global_context.global_context(self.get_friendly_name())
		global_environment = environment(self.global_context)
		global_func = mcfunction(global_environment)
		
		self.global_context.scale = parsed['scale']

		for assignment in parsed["assignments"]:
			if not self.compile(global_func, assignment):
				print "Error compiling assignment at line {0}".format(get_line(assignment))
				return False

		for section in parsed['sections']:
			type, id, template_params, params, sub = section
			if type == 'macro':
				self.macros[id] = (params, sub)
			elif type == 'template_function':
				self.template_functions[id] = (template_params, params, sub)
				
		for section in parsed["sections"]:
			if section[0] == 'macro' or section[0] == 'template_function':
				continue
			if not self.compile_section(section, global_environment):
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
		
	def compile_section(self, section, environment):
		type, name, template_params, params, lines = section

		if type == 'function':
			f = mcfunction(environment.clone(new_function_name = name), True, params)
		else:
			f = mcfunction(environment.clone(new_function_name = name))
			
		self.global_context.register_function(name, f)

		if type == 'clock':
			self.global_context.register_clock(name)
			
		if not self.compile_block(f, lines):
			return False
				
		return True
	
	def compile_block(self, func, lines):
		for line in lines:
			try:
				if not self.compile(func, line):
					print 'Unable to compile block at line {0}'.format(get_line(line))
					return False
			except Exception as e:
				print('Exception while compiling block at line {}'.format(get_line(line)))
				raise
			
		
		return True
		
	def compile(self, func, line):
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
				func.environment.set_dollarid(id, eval(python, globals(), func.environment.get_python_env()))
			except:
				print('Could not evaluate "{0}" at line {1}'.format(python, get_line(line)))
				return False
			
		elif type == 'For':
			identifier, setpython, sub = content
			
			try:
				set = eval(setpython, globals(), func.environment.get_python_env())
			except:
				print('Could not evaluate "{0}" in "for" block at line {1}'.format(setpython, get_line(line)))
				return False
			
			try:
				iter(set)
			except:
				print '"{0}" in "for" block at line {1} is not an iterable set.'.format(setpython, get_line(line))
				return False

			for v in set:
				func.environment.set_dollarid(identifier, v)
				if not self.compile_block(func, sub):
					return False
			
		elif type == 'SelectorAssignment':
			id, fullselector = content
			
			func.environment.set_atid(id, fullselector)
			
		elif type == 'SelectorDefinition':
			id, fullselector, items = content
			
			selector = func.environment.set_atid(id, fullselector)
			
			for type, val in items:
				if type == 'Tag':
					selector.tag = val
				elif type == 'Path':
					path_id, path, data_type, scale = val
					if scale == None:
						scale = self.global_context.scale
					selector.paths[path_id] = (path, data_type, scale)
				elif type == 'VectorPath':
					vector_id, path, data_type, scale = val
					if scale == None:
						scale = self.global_context.scale
					selector.vector_paths[vector_id] = (path, data_type, scale)
				elif type == 'Method':
					sub_env = func.environment.clone()
					sub_env.update_self_selector('@'+id)
					if not self.compile_section(val, sub_env):
						return False
				else:
					print('Unknown selector item type "{0}" in selector definition at line {1}'.format(type, get_line(line)))
					return False
					
		elif type == 'BlockTag':
			name, blocks = content
			self.global_context.register_block_tag(name, blocks)
			
		elif type == 'ArrayDefinition':
			name, from_val, to_val = content
			
			from_val = int(func.environment.apply_replacements(from_val))
			to_val = int(func.environment.apply_replacements(to_val))

			vals = list(range(from_val, to_val))
			
			for i in vals:
				self.global_context.register_objective('{}{}'.format(name, i))
			
			valvar = '{}Val'.format(name)
			self.global_context.register_objective(valvar)
			
			indexvar = '{}Idx'.format(name)
			self.global_context.register_objective(indexvar)
			
			line = get_line(line)

			get_func = mcfunction(func.environment.clone())
			get_func_name = 'array_{}_get'.format(name.lower())
			self.global_context.register_function(get_func_name, get_func)
			cases = [(i, i, [('Command', '/scoreboard players operation Global {} = Global {}{}'.format(valvar, name, i))], line, None) for i in vals]
			if not self.switch_cases(get_func, indexvar, cases, 'arrayget', 'arraygetidx'):
				return False
			
			set_func = mcfunction(func.environment.clone())
			set_func_name = 'array_{}_set'.format(name.lower())
			self.global_context.register_function(set_func_name, set_func)
			cases = [(i, i, [('Command', '/scoreboard players operation Global {}{} = Global {}'.format(name, i, valvar))], line, None) for i in vals]
			if not self.switch_cases(set_func, indexvar, cases, 'arrayset', 'arraysetidx'):
				return False
				
			self.global_context.register_array(name, from_val, to_val)
			
		elif type == 'Create':
			atid, relcoords = content
			
			if not self.run_create(func, atid, relcoords):
				print('Error creating entity at line {0}'.format(get_line(line)))
				return False
			
		elif type == 'ArrayAssignment':
			name, (idxtype, idxval), expr = content
			
			if name not in self.global_context.arrays:
				print('Tried to assign to undefined array "{}"'.format(name))
				return False
			
			if idxtype == 'Const':
				array_var = self.get_arrayconst_var(func, name, idxval)
				
				id = self.calc_math(func, expr, assignto=array_var)
				
				if id == None:
					print('Unable to compute value for array assignment at line {}'.format(get_line(line)))
					return False
					
				if id != array_var:
					func.add_command('scoreboard players operation Global {} = Global {}'.format(array_var, id))
					
				func.environment.scratch.free_scratch(id)
			
			elif idxtype == 'Expr':
				val_var = '{}Val'.format(name)
				id1 = self.calc_math(func, expr, assignto=val_var)
				
				if id1 == None:
					print('Unable to compute value for array assignment at line {}'.format(get_line(line)))
					return False
				
				idx_var = '{}Idx'.format(name)
				
				id2 = self.calc_math(func, idxval, assignto=idx_var)
				if id2 == None:
					print('Unable to calculate array index at line {}'.format(get_line(line)))
					return False
					
				if id1 != val_var:
					func.add_command('scoreboard players operation Global {} = Global {}'.format(val_var, id1))
				
				if id2 != idx_var:
					func.add_command('scoreboard players operation Global {} = Global {}'.format(idx_var, id2))
					
				func.add_command('function {}:array_{}_set'.format(self.namespace, name.lower()))
				
				func.environment.scratch.free_scratch(id1)
				func.environment.scratch.free_scratch(id2)
		
		elif type == 'ScoreboardAssignment':
			var, op, expr = content
			
			if op in ['+=', '-=', '*=', '/=', '%=']:
				modify = True
			else:
				modify = False
			
			(raw_selector, objective) = self.get_variable(func, var, initialize = modify)
			
			selector = func.environment.apply(raw_selector)
			
			if op in ['+=', '-=', '='] and expr[0] == 'NUM' or expr[0] == 'SCALE':
				if expr[0] == 'NUM':
					operand = func.environment.apply(expr[1])
				else:
					operand = self.global_context.scale
				
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
					operand = func.environment.apply(expr[1])
				elif expr[0] == 'SCALE':
					operand = self.global_context.scale
				
				if not isNumber(operand):
					print "Unable to apply {0} to {1} at line {2}.".format(op, operand, get_line(line))
					return False
					
				operand = int(operand)
			
				id2 = self.global_context.add_constant(operand)
				command = "/scoreboard players operation {0} {1} {2} {3} {4}".format(selector, objective, op, id2, "Constant")
				
				func.add_command(command)
				
				self.set_variable(func, var)
				
			elif op == '=' and expr[0] == 'Selector':
				target = expr[1]
				
				if not func.check_single_entity(target):
					print('Selector "{0}" not limited to a single entity at line {1}'.format(target, get_line(line)))
					return False
			
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
								
				if not self.run_create(func, atid, relcoords):
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
					
				result = self.calc_math(func, expr, assignto=assignto)

				if result == None:
					print 'Unable to compile assignment operand for {0} {1} {2} at line {3}.'.format(selector, objective, op, get_line(line))
					return False
					
				if selector != 'Global' or result != objective or op != '=':
					func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(selector, objective, op, result))
					
				func.environment.scratch.free_scratch(result)

			self.set_variable(func, var)
			
		elif type == 'VectorAssignment' or type == 'VectorAssignmentScalar':
			var, op, expr = content
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
					sel, id = self.get_variable(func, components[i], initialize = modify)
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
				component_val_vars = self.calc_vector_math(func, expr, assignto)
				if component_val_vars == None:
					print('Unable to compute vector assignment at line {0}'.format(get_line(line)))
					return False
			elif type == 'VectorAssignmentScalar':
				val_var = self.calc_math(func, expr)			
				component_val_vars = [val_var for i in range(3)]

			if var_type == 'VAR_ID':
				for i in range(3):
					var_name = '_{0}_{1}'.format(var_content, i)
					if var_name != component_val_vars[i]:
						func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(var_name, op, component_val_vars[i]))
					self.global_context.register_objective(var_name)
					
			elif var_type == 'SEL_VAR_ID':
				sel, id = var_content

				if op != '=':
					temp_vars = func.environment.scratch.get_scratch_vector()
					if func.get_vector_path(sel, id, temp_vars):
						for i in range(3):
							func.add_command('scoreboard players operation Global {0} {1} Global {2}'.format(temp_vars[i], op, component_val_vars[i]))
					
						component_val_vars = temp_vars
					else:
						for var in temp_vars:
							func.environment.scratch.free_scratch(var)
					
				if not func.set_vector_path(sel, id, component_val_vars):
					for i in range(3):
						var = '_{0}_{1}'.format(id, i)
						self.global_context.register_objective(var)
						func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, var, op, component_val_vars[i]))

			elif var_type == 'VAR_COMPONENTS':
				components = var_content
			
				for i in range(3):
					sel, id = component_vars[i]
					var = components[i]
					
					if sel != 'Global' or id != component_val_vars[i]:
						func.add_command('scoreboard players operation {0} {1} {2} Global {3}'.format(sel, id, op, component_val_vars[i]))
						
					self.set_variable(func, var)
					
			else:
				print('Unknown vector variable type "{0}" at line {1}'.format(var_type, get_line(line)))
				return False

			for i in range(3):
				func.environment.scratch.free_scratch(component_val_vars[i])

		elif type == 'Execute' or type == 'While':
			exec_func = mcfunction(func.environment.clone())
			
			exec_items, sub = content
			
			cmd = self.get_execute_command(exec_items, func, exec_func)
			if cmd == None:
				print('Unable to compile {0} block at line {1}'.format(type.lower(), get_line(line)))
			
			if not self.compile_block(exec_func, sub):
				return False


			single = exec_func.single_command()
			if single == None or type == 'While':
				unique = self.global_context.get_unique_id()
				func_name = '{0}{1:03}_ln{2}'.format(type.lower(), unique, get_line(line))
				self.global_context.register_function(func_name, exec_func)
				func.add_command('{0}run function {1}:{2}'.format(cmd, self.namespace, func_name))
				
				if type == 'While':
					dummy_func = mcfunction(exec_func.environment.clone())
					sub_cmd = self.get_execute_command(exec_items, exec_func, dummy_func)
					if sub_cmd == None:
						print('Unable to compile {0} block at line {1}'.format(type.lower(), get_line(line)))

					exec_func.add_command('{0}run function {1}:{2}'.format(cmd, self.namespace, func_name))
			else:
				if single.startswith('/'):
					single = single[1:]
					
				if single.startswith('execute '):
					func.add_command(cmd + single[len('execute '):])
				else:
					func.add_command(cmd + 'run ' + single)

				
		elif type == 'ForSelector':
			id, selector, sub = content
			
			scratch_id = func.environment.scratch.get_scratch()
			
			exec_func = mcfunction(func.environment.clone())
			
			combined_selector = selector_definition(selector, func.environment)
			combined_selector.scores_min[scratch_id] = 1
			combined_selector.set_part('limit', '1')
			exec_func.environment.selectors[id] = combined_selector
			exec_func.environment.update_self_selector(selector)
			
			func.add_command('scoreboard players set {0} {1} 0'.format(selector, scratch_id))
			exec_func.add_command('scoreboard players set @s {0} 1'.format(scratch_id))
			if not self.compile_block(exec_func, sub):
				return False
			exec_func.add_command('scoreboard players set @s {0} 0'.format(scratch_id))
			
			func.environment.scratch.free_scratch(scratch_id)
			
			unique = self.global_context.get_unique_id()
			exec_name = 'for{0:03}_ln{1}'.format(unique, get_line(line))
			self.global_context.register_function(exec_name, exec_func)
			
			func.add_command('execute as {0} run function {1}:{2}'.format(selector, self.namespace, exec_name))
				
		elif type == 'If':
			ifpython, sub, else_sub = content
			
			try:
				condition = eval(ifpython, globals(), func.environment.get_python_env())
			except:
				print('Could not evaluate "{0}" in "if" block at line {1}'.format(ifpython, get_line(line)))
				return False
		
			if condition:
				if not self.compile_block(func, sub):
					return False

		elif type == 'ForIndex':
			var, fr, to, by, sub = content
			
			self.global_context.register_objective(var)
			
			from_var = self.calc_math(func, fr, var)
			if from_var != var:
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(var, from_var))

			to_scratch = func.environment.scratch.get_scratch()
			to_var = self.calc_math(func, to, to_scratch)
			if to_var != to_scratch:
				func.add_command('scoreboard players operation Global {0} = Global {1}'.format(to_scratch, to_var))
				
			if by != None:
				by_scratch = func.environment.scratch.get_scratch()
				by_var = self.calc_math(func, by, by_scratch)
				if by_var != by_scratch:
					func.add_command('scoreboard players operation Global {0} = Global {1}'.format(by_scratch, by_var))
					
			unique = self.global_context.get_unique_id()
			loop_func_name = 'for{0:03}_ln{1}'.format(unique, get_line(line))
			
			new_env = func.environment.clone()
			loop_func = mcfunction(new_env)
			self.global_context.register_function(loop_func_name, loop_func)	
			
			if not self.compile_block(loop_func, sub):
				return False
			
			if by == None:
				continue_command = 'execute if score Global {0} <= Global {1} run function {2}:{3}'.format(var, to_scratch, self.namespace, loop_func_name)
				func.add_command(continue_command)
				loop_func.add_command('scoreboard players add Global {0} 1'.format(var))
				loop_func.add_command(continue_command)
			else:
				continue_negative_command = 'execute if score Global {0} matches ..-1 if score Global {1} >= Global {2} run function {3}:{4}'.format(by_scratch, var, to_scratch, self.namespace, loop_func_name)
				continue_positive_command = 'execute if score Global {0} matches 1.. if score Global {1} <= Global {2} run function {3}:{4}'.format(by_scratch, var, to_scratch, self.namespace, loop_func_name)
				func.add_command(continue_negative_command)
				func.add_command(continue_positive_command)
				loop_func.add_command('scoreboard players operation Global {0} += Global {1}'.format(var, by_scratch))
				loop_func.add_command(continue_negative_command)
				loop_func.add_command(continue_positive_command)				
				
			func.environment.scratch.free_scratch(to_scratch)
			if by != None:
				func.environment.scratch.free_scratch(by_scratch)

		elif type == 'Switch':
			expr, cases_raw = content
			
			result = self.calc_math(func, expr)
			if result == None:
				print('Unable to compute switch expression at line {}'.format(get_line(line)))
				return False

			cases = []
			for case in cases_raw:
				type, content = case
				line = get_line(case)
				if type == 'range':
					vmin, vmax, sub = content
					vmin = int(func.environment.apply_replacements(vmin))
					vmax = int(func.environment.apply_replacements(vmax))
					cases.append((vmin, vmax, sub, line, None))
				elif type == 'python':
					dollarid, python, sub = content
					try:
						vals = eval(python, globals(), func.environment.get_python_env())
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
				
			if not self.switch_cases(func, result, cases):
				return False
					
			func.environment.scratch.free_scratch(result)
				
		elif type == 'Call':
			dest, params = content
			
			if not self.evaluate_params(func, params):
				return False
			
			func.add_command('function {0}:{1}'.format(self.namespace, dest))
		
		elif type == 'MethodCall':
			selector, dest, params = content
			
			if not self.evaluate_params(func, params):
				return False
			
			if selector == '@s':
				func.add_command('function {0}:{1}'.format(self.namespace, dest))
			else:
				func.add_command('execute as {0} run function {1}:{2}'.format(selector, self.namespace, dest))
			
		elif type == 'MacroCall':
			macro, args = content
			
			if macro not in self.macros:
				print('Line {1}: macro "{0}" does not exist'.format(macro, get_line(line)))
				return False
				
			params, sub = self.macros[macro]
				
			if len(args) != len(params):
				print('Tried to call Macro "{0}" with {1} arguments at line {3}, but it requires {2}'.format(macro, len(args), len(params), get_line(line)))
				return False
				
			new_env = func.environment.clone()
				
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
					
			old_env = func.environment
			func.environment = new_env
			if not self.compile_block(func, sub):
				return False
			func.environment = old_env
			
		elif type == 'TemplateFunctionCall':
			function, template_args, args = content
			
			if function not in self.template_functions:
				print('Tried to call non-existant template function "{}" at line {}'.format(function, get_line(line)))
				return False
			
			template_params, params, sub = self.template_functions[function]
			
			if len(template_args) != len(template_params):
				print('Tried to call template function "{}" with {} template arguments at line {}'.format(function, len(template_args), get_line(line)))
				return False
				
			if len(args) != len(params):
				print('Tried to call template function "{}" with {} function arguments at line {}'.format(function, len(args), get_line(line)))
				return False
			
			# Get textual function name
			func_name = function
			for template_arg in template_args:
				template_arg_val = func.environment.apply_replacements(template_arg)
				func_name = func_name + '_{}'.format(template_arg_val)
			
			# Calculate function arguments
			for i in range(len(args)):
				id = self.calc_math(args[i])
				if id == None:
					print('Unable to compute argument "{}" for template function "{}" at line {}'.format(params[i], function, get_line(line)))
					return False
				func.add_command('scoreboard players operation Global Param{} = Global {}'.format(i, id))
				func.environment.scratch.free_scratch(id)
			
			# Compile the function if it doens't exist yet
			if func_name not in self.global_context.functions:
				new_env = func.environment.clone()
				
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
				if not self.compile_block(new_func, sub):
					return False
				
				# Register the new function
				self.global_context.register_function(func_name, new_func)
				
			func.add_command('function {}:{}'.format(self.namespace, func_name))
		
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
		
	def switch_cases(self, func, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
		if len(cases) == 1:
			vmin, vmax, sub, line, dollarid = cases[0]
			if dollarid != None:
				func.environment.set_dollarid(dollarid, vmin)
			if not self.compile_block(func, sub):
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
				sub_env = func.environment.clone()
				case_func = mcfunction(sub_env)
				
				if len(sub_cases) == 1:
					vmin, vmax, sub, line, dollarid = sub_cases[0]
					if dollarid != None:
						case_func.environment.set_dollarid(dollarid, vmin)
					if not self.compile_block(case_func, sub):
						return False
						
					single_command = case_func.single_command()
					if single_command != None:
						if single_command.startswith('/'):
							single_command = single_command[1:]
							
						func.add_command('execute if score Global {} matches {}..{} run {}'.format(var, vmin, vmax, single_command))
					else:
						unique = self.global_context.get_unique_id()

						if vmin == vmax:
							case_name = '{}{}_{:03}_ln{}'.format(case_func_name, vmin, unique, line)
						else:
							case_name = '{}{}-{}_{:03}_ln{}'.format(case_func_name, vmin, vmax, unique, line)
							
						func.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, self.namespace, case_name))
						self.global_context.register_function(case_name, case_func)
				else:
					unique = self.global_context.get_unique_id()
					case_name = '{}{}-{}_{:03}_ln{}'.format(switch_func_name, vmin, vmax, unique, line)
					func.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, self.namespace, case_name))
					self.global_context.register_function(case_name, case_func)
				
					if not self.switch_cases(case_func, var, sub_cases):
						return False
				
		return True

	def get_execute_command(self, exec_items, func, exec_func):	
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
				cmd += self.get_if_chain(func, val)
			if type == 'Unless':
				cmd += self.get_if_chain(func, val, 'unless')
			elif type == 'As':
				cmd += 'as {0} '.format(val)
				exec_func.environment.update_self_selector(val)
			elif type == 'AsId':
				var, attype = val
				
				selector, id = self.get_variable(func, var, initialize = True)
				
				self.global_context.register_objective('_id')
				self.global_context.register_objective(id)
				
				func.add_command('scoreboard players operation Global _id = {0} {1}'.format(selector, id))
									
				cmd += 'as @e if score @s _id = Global _id '.format(selector, id)
				
				if attype != None:
					exec_func.environment.update_self_selector('@' + attype)
				else:
					exec_func.environment.update_self_selector('@s')
			elif type == 'AsCreate':
				if len(exec_items) > 1:
					print('"as create" must be its own block at line {0}'.format(get_line(line)))
					return None
					
				atid, relcoords = val
				
				self.global_context.register_objective('_age')
				func.add_command('scoreboard players add @e _age 1')
				
				if not self.run_create(func, atid, relcoords):
					print('Error creating entity for "as" block at line {0}'.format(get_line(line)))
					return None
					
				func.add_command('scoreboard players add @e _age 1')
				cmd += 'as @e[_age==1] '
				
				exec_func.environment.update_self_selector('@'+atid)
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
					scale = self.global_context.scale

				vec_vals = self.calc_vector_math(func, expr)
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
		
	def get_if_chain(self, func, conditions, iftype='if'):
		test = ''
		for type, val in conditions:
			if type == 'selector':
				test += '{0} entity {1} '.format(iftype, val)
			elif type == 'score':
				var, op, (rtype, rval) = val
				
				lselector, lvar = self.get_variable(func, var, initialize = True)
				
				self.global_context.register_objective(lvar)
				func.get_path(lselector, lvar)
				
				if rtype == 'num':
					rval = func.environment.apply_replacements(rval)
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
					rselector, rvar = self.get_variable(func, rval, initialize = True)
					
					self.global_context.register_objective(rvar)
					func.get_path(rselector, rvar)
					test += '{0} score {1} {2} {3} {4} {5} '.format(iftype, lselector, lvar, op, rselector, rvar)
					
			elif type == 'pointer':
				var, rselector = val
				
				lselector, id = self.get_variable(func, var, initialize = True)
				
				self.global_context.register_objective(id)
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
				if block in self.global_context.block_tags:
					block = '#{0}:{1}'.format(self.namespace, block)
				else:
					block = 'minecraft:{0}'.format(block)
				test += '{0} block {1} {2} '.format(iftype, ' '.join(relcoords), block)
			else:
				print('Unknown "if" type: {0}'.format(type))
				return None
		
		return test
	
					
	def run_create(self, func, atid, relcoords):
		if atid not in func.environment.selectors:
			print('Unable to create unknown entity: @{0}'.format(atid))
			return False
		
		selector = func.environment.selectors[atid]
		
		entity_type = selector.get_type()
		
		if entity_type == None:
			print('Unable to create @{0}, no entity type is defined.'.format(atid))
			return False
			
		if selector.tag == None:
			func.add_command('summon {0} {1}'.format(entity_type, ' '.join(relcoords)))
		else:
			func.add_command('summon {0} {1} {2}'.format(entity_type, ' '.join(relcoords), selector.tag))
			
		return True
		
	def get_selector_name(self, s):
		if '[' in s:
			s = s.split('[')[0]
		if s[0] == '@':
			s = s[1:]
		return s.lower()
	
	def evaluate_params(self, func, params):
		results = []
		for p in range(len(params)):
			param_name = 'Param{0}'.format(p)
			val = self.calc_math(func, params[p])
			func.add_operation('Global', 'Param{0}'.format(p), '=', val)
		
		return True
	
	def calc_vector_math(self, func, expr, assignto=None):
		type, content = expr
		
		if type == 'VECTOR':
			exprs = content
			vars = []
			for i in range(3):
				if assignto == None:
					var = self.calc_math(func, exprs[i])
				else:
					var = self.calc_math(func, exprs[i], assignto[i])
					
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
				self.global_context.register_objective(component_name)
			
			return return_components
			
		elif type == 'SEL_VECTOR_VAR':
			sel, id = content
			
			return_components = []
			for i in range(3):
				if assignto != None:
					return_components.append(assignto[i])
				else:
					return_components.append(func.environment.scratch.get_scratch())
			
			if not func.get_vector_path(sel, id, return_components):
				for i in range(3):
					var = '_{0}_{1}'.format(id, i)
					self.global_context.register_objective(var)
					func.add_command('scoreboard players operation Global {0} = {1} {2}'.format(return_components[i], sel, var))
			
			return return_components
		
		elif type == 'VECTOR_BINOP_VECTOR' or type == 'VECTOR_BINOP_SCALAR':
			lhs, op, rhs = content
			
			return_components = []
			
			left_component_vars = self.calc_vector_math(func, lhs, assignto)
			if left_component_vars == None:
				return None
				
			for i in range(3):
				if func.environment.scratch.is_scratch(left_component_vars[i]):
					return_components.append(left_component_vars[i])
				elif assignto != None and left_component_vars[i] == assignto[i]:
					return_components.append(left_component_vars[i])
				else:
					newId = func.environment.scratch.get_scratch()
					func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, left_component_vars[i]))
					return_components.append(newId)
			
			if type == 'VECTOR_BINOP_VECTOR':
				right_component_vars = self.calc_vector_math(func, rhs)
				if right_component_vars == None:
					return None
					
				for i in range(3):
					func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], op, right_component_vars[i]))
					func.environment.scratch.free_scratch(right_component_vars[i])
			
			if type == 'VECTOR_BINOP_SCALAR':
				right_var = self.calc_math(func, rhs)
				if right_var == None:
					return None
				
				for i in range(3):
					func.add_command('scoreboard players operation Global {0} {1}= Global {2}'.format(return_components[i], op, right_var))
					
				func.environment.scratch.free_scratch(right_var)
			
			return return_components	
		
		if type == 'VECTOR_HERE':
			scale = content
			if scale == None:
				scale = self.global_context.scale
			
			self.global_context.register_objective('_age')
			func.add_command('scoreboard players add @e _age 1')
			func.add_command('summon area_effect_cloud')
			func.add_command('scoreboard players add @e _age 1')
			
			return_components = []
			for i in range(3):
				if assignto != None:
					return_components.append(assignto[i])
				else:
					return_components.append(func.environment.scratch.get_scratch())
			
				func.add_command('execute store result score Global {0} run data get entity @e[_age==1,limit=1] Pos[{1}] {2}'.format(return_components[i], i, scale))
			
			func.add_command('/kill @e[_age==1]')
			
			return return_components

	def calc_math(self, func, expr, assignto = None):
		etype = expr[0]
		
		if etype == 'SELVAR':
			self.global_context.register_objective(expr[2])
			
			func.get_path(expr[1], expr[2])
			
			if assignto != None:
				newId = assignto
			elif expr[1] != 'Global':
				newId = func.environment.scratch.get_scratch()
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
			
				id1 = self.calc_math(func, left, assignto=assignto)
				if id1 == None:
					print "Unable to compile LHS of binop {0}".format(type)
					return None
				
				id1 = self.get_modifiable_id(func, id1, assignto)
					
				if right[0] == 'NUM' or right[0] == 'SCALE':
					if right[0] == 'NUM':
						val = func.environment.apply_replacements(right[1])
						operand2 = int(val)
							
					elif right[0] == 'SCALE':
						operand2 = int(self.global_context.scale)
						
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
						id2 = self.global_context.add_constant(operand2)
						func.add_command('scoreboard players operation Global {0} {1}= {2} Constant'.format(id1, type, id2))
				elif right[0] == 'SELVAR':
					self.global_context.register_objective(right[2])
			
					func.get_path(right[1], right[2])
						
					func.add_command('scoreboard players operation Global {} {}= {} {}'.format(id1, type, right[1], right[2]))
					
					return id1
					
				else:
					id2 = self.calc_math(func, right)
					if id2 == None:
						print "Unable to compile RHS of binop {0}".format(type)
						return None
					
					func.add_operation('Global', id1, type+'=', id2)
					if func.environment.scratch.is_scratch(id2):
						func.environment.scratch.free_scratch(id2)
				
				return id1
				
			if type == "^":
				target = self.calc_math(func, expr[2], assignto=assignto)
				
				if target == None:
					print 'Unable to compile exponent for ^'
					return None
				
				power = int(expr[3])
				
				if power < 1:
					print "Powers less than 1 are not supported"
					return None
					
				if power == 1:
					return target
				
				newId = func.environment.scratch.get_scratch()
				func.add_operation('Global', newId, '=', target)
				
				for i in xrange(power-1):
					func.add_operation('Global', newId, '*=', target)
					
				return newId
				
			print "Binary operation '{0}' isn't implemented".format(type)
			return None
			
		if etype == 'DOT':
			lhs = self.calc_vector_math(func, expr[1])
			rhs = self.calc_vector_math(func, expr[2])
			
			prods = []
			for i in range(3):
				prod = lhs[i]
				if not func.environment.scratch.is_scratch(prod):
					prod = func.environment.scratch.get_scratch()
					func.add_command('scoreboard players operation Global {0} = Global {1}'.format(prod, lhs[i]))
				func.add_command('scoreboard players operation Global {0} *= Global {1}'.format(prod, rhs[i]))
				
				prods.append(prod)
				
			func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[1]))
			func.add_command('scoreboard players operation Global {0} += Global {1}'.format(prods[0], prods[2]))
			
			for i in range(3):
				for vec in [lhs, rhs, prod]:
					if vec[i] != prods[0]:
						func.environment.scratch.free_scratch(vec[i])
			
			return prods[0]
			
		if etype == 'NUM' or etype == 'SCALE': 
			if assignto != None:
				id = assignto
			else:
				id = func.environment.scratch.get_scratch()
				
			if etype == 'NUM':
				val = expr[1]
			elif etype == 'SCALE':
				val = self.global_context.scale
				
			func.add_command("/scoreboard players set Global {0} {1}".format(id, val))
			
			return id
			
		if etype == 'ARRAYCONST':
			array_var = self.get_arrayconst_var(func, expr[1], expr[2])
			
			return array_var
			
		if etype == 'ARRAYEXPR':
			array = expr[1]
			
			if array not in self.global_context.arrays:
				print('Tried to use undefined array "{}"'.format(array))
				return None
				
			index_var = '{}Idx'.format(array)
			id = self.calc_math(func, expr[2], assignto=index_var)
			if id == None:
				return None
			
			if id != index_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
				
			func.add_command('function {}:array_{}_get'.format(self.namespace, array.lower()))
			
			func.environment.scratch.free_scratch(id)
			
			return '{}Val'.format(array)
			
		if etype == 'UNARY':
			type = expr[1]
			if type == "-":
				id = self.calc_math(func, expr[2], assignto)
				
				if id == None:
					return None
				
				id = self.get_modifiable_id(func, id, assignto)

				self.global_context.add_constant(-1)
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
				
				id = self.calc_math(func, args[0])
				if id == None:
					print 'Unable to compile argument for sqrt'
					return None
				
				guess = self.calc_math(func, scriptparse.parse("20")[1])
				
				if guess == None:
					print 'Unable to compile initial guess for sqrt algorithm'
					return None
					
				for iteration in xrange(15):
					newId = func.environment.scratch.get_scratch()
					func.add_command('scoreboard players operation Global {0} = Global {1}'.format(newId, id))
					guess = self.calc_math(func, scriptparse.parse("({0}/{1}+{1})/2".format(newId, guess))[1])
					if guess == None:
						print 'Unable to compile guess iteration for sqrt algorithm'
						return None
				
				return guess

			elif efunc == 'abs':
				if len(args) <> 1:
					print "abs takes exactly 1 argument, received: {0}".format(args)
					return None

				id = self.calc_math(func, args[0], assignto=assignto)
				if id == None:
					print 'Unable to compile argument for abs function'
					return None
				
				id = self.get_modifiable_id(func, id, assignto)
			
				self.global_context.add_constant(-1)
				func.add_command("execute if score Global {0} matches ..-1 run scoreboard players operation Global {0} *= minus Constant".format(id))
				
				return id
				
			elif efunc == 'rand':
				if len(args) == 1:
					min = 0
					if args[0][0] == 'NUM':
						max = func.environment.apply(args[0][1])
						if not isNumber(max):
							print "Argument '{0}' to rand is not an integer.".format(args[0][1])
							return None
						max = int(max)
					else:
						print "Function 'rand' accepts only integer arguments."
						return None
				elif len(args) == 2:
					if args[0][0] == 'NUM':
						min = func.environment.apply(args[0][1])
						if not isNumber(min):
							print "Argument '{0}' to rand is not an integer.".format(args[0][1])
							return None
						min = int(min)
					else:
						print "Function 'rand' accepts only integer arguments."
						return None
					if args[1][0] == 'NUM':
						max = func.environment.apply(args[1][1])
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

				id = func.environment.scratch.get_scratch()
				func.add_command("scoreboard players set Global {0} 0".format(id))
				
				first = True
				for f in factor(span):
					self.global_context.allocate_rand(f)
					
					if first:
						first = False
					else:
						c = self.global_context.add_constant(f)
						func.add_command("scoreboard players operation Global {0} *= {1} Constant".format(id, c))
					
					rand_stand = '@e[type=armor_stand, {0} <= {1}, limit=1, sort=random]'.format(self.get_random_objective(), f-1)
					rand_stand = func.environment.apply(rand_stand)
					func.add_command("scoreboard players operation Global {0} += {1} {2}".format(id, rand_stand, self.get_random_objective()))
				
				if min > 0:
					func.add_command("/scoreboard players add Global {0} {1}".format(id, min))
				if min < 0:
					func.add_command("/scoreboard players remove Global {0} {1}".format(id, -min))
					
				return id

			elif efunc == 'sin' or efunc == 'cos':
				if len(args) <> 1:
					print "{0} takes exactly 1 argument, received: {1}".format(efunc, args)
					return None
				
				id = self.calc_math(func, args[0])
				if id == None:
					print 'Unable to compile argument for {0} function'.format(efunc)
					return None
					
				moddedId2 = func.environment.scratch.get_temp_var()
				if efunc == 'sin':
					modret = self.calc_math(func, scriptparse.parse("(({0}%360)+360)%360".format(id))[1], assignto=moddedId2)
				else:
					modret = self.calc_math(func, scriptparse.parse("(({0}%360)+450)%360".format(id))[1], assignto=moddedId2)
				if modret == None:
					print 'Unable to compile modulus math for {0} function'.format(efunc)
					return None
				if modret != moddedId2:
					func.add_command('scoreboard players operation Global {0} = Global {1}'.format(moddedId2, modret))
					
				id = self.get_modifiable_id(func, id, assignto)
				
				modId = func.environment.scratch.get_temp_var()
				func.add_operation('Global', modId, '=', moddedId2)
				c180 = self.global_context.add_constant(180)
				func.add_command("/scoreboard players operation Global {0} %= {1} Constant".format(modId, c180))
				
				parsed = scriptparse.parse("4000*{0}*(180-{0})/(40500-{0}*(180-{0}))".format(modId))
				retId = self.calc_math(func, parsed[1], assignto=assignto)
				if retId == None:
					print 'Unable to compile estimator for {0} function'.format(efunc)
					return None
				
				self.global_context.add_constant(-1)
				func.add_command("/execute if score Global {0} matches 180.. run scoreboard players operation Global {1} *= minus Constant".format(moddedId2, retId))
				
				func.environment.scratch.free_temp_var(modId)
				func.environment.scratch.free_temp_var(moddedId2)
				
				return retId
			
			else:
				if not self.evaluate_params(func, args):
					return False
				
				func.add_command('/function {0}:{1}'.format(self.namespace, efunc))
				
				return "ReturnValue"
			
			return None
				
		print "Unable to interpret math block."
		
		return None

	def get_arrayconst_var(self, func, name, idxval):
		if name not in self.global_context.arrays:
			print('Tried to use undefined array "{}"'.format(name))
			return None
			
		from_val, to_val = self.global_context.arrays[name]
		
		index = int(func.environment.apply_replacements(idxval))
		
		if index < from_val or index >= to_val:
			if from_val == 0:
				print('Tried to index {} outside of array {}[{}]'.format(index, name, to_val))
			else:
				print('Tried to index {} outside of array {}[{} to {}]'.format(index, name, from_val, to_val))

		return '{}{}'.format(name, index)
				
	def get_variable(self, func, variable, initialize):
		type, content = variable
		
		if type == 'Var':
			id, var = content
			
			if initialize:
				func.get_path(id, var)
				
			self.global_context.register_objective(var)
			
			return content
			
		if type == 'ArrayConst':
			name, idxval = content
			
			array_var = self.get_arrayconst_var(func, name, idxval)
			
			return 'Global', array_var
			
		if type == 'ArrayExpr':
			name, idx_expr = content
			
			if name not in self.global_context.arrays:
				print('Tried to use undefined array "{}"'.format(name))
				return None
				
			index_var = '{}Idx'.format(name)
			id = self.calc_math(func, idx_expr, assignto=index_var)
			if id == None:
				raise Exception('Unable to calculate array "{}" index'.format(name))
			
			if id != index_var:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
				
			if initialize:
				func.add_command('function {}:array_{}_get'.format(self.namespace, name.lower()))
			
			func.environment.scratch.free_scratch(id)
			
			return 'Global', '{}Val'.format(name)
		
		else:
			raise Exception('Tried to get unknown variable type "{}"'.format(type))

			
	def set_variable(self, func, variable):
		type, content = variable
		
		if type == 'Var':
			id, var = content
			func.set_path(id, var)
			
		elif type == 'ArrayExpr':
			name, idx_expr = content
			func.add_command('function {}:array_{}_set'.format(self.namespace, name.lower()))
		
	# Takes a scoreboard objective and returns a (potentially different)
	# scoreboard objective which can be freely modified.
	def get_modifiable_id(self, func, id, assignto):
		if assignto != None:
			if id != assignto:
				func.add_operation('Global', assignto, '=', id)
				id = assignto
		elif not func.environment.scratch.is_scratch(id):
			newId = func.environment.scratch.get_scratch()
			func.add_operation('Global', newId, '=', id)
			id = newId
			
		return id
		
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
			objective = self.get_random_objective()
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