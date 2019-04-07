from selector_definition import selector_definition
from environment import isNumber
from source_file import source_file
import math
import traceback

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
		
	f.compile_blocks(lines)

class mcfunction(object):
	def __init__(self, environment, callable = False, params = []):
		self.commands = []
		self.environment = environment
		self.params = params
		self.callable = callable
		self.environment_stack = []
		
		for param in params:
			self.register_local(param)

	# Takes a scoreboard objective and returns a (potentially different)
	# scoreboard objective which can be freely modified.
	def get_modifiable_id(self, id, assignto):
		if assignto != None:
			if id != assignto:
				self.add_operation('Global', assignto, '=', id)
				id = assignto
		elif not self.is_scratch(id):
			newId = self.get_scratch()
			self.add_operation('Global', newId, '=', id)
			id = newId
			
		return id
	
	def evaluate_params(self, params):
		results = []
		for p in range(len(params)):
			param_name = 'Param{0}'.format(p)
			try:
				val = params[p].compile(self, None)
			except Exception as e:
				print(e)
				print('Unable to compile parameter {}.'.format(p))
				return False
			self.add_operation('Global', 'Param{0}'.format(p), '=', val)
		
		return True			

	def get_variable(self, variable, initialize):
		type, content = variable
		
		if type == 'Var':
			id, var = content
			
			if initialize:
				self.get_path(id, var)
				
			self.register_objective(var)
			
			return content
			
		if type == 'ArrayConst':
			name, idxval = content
			
			array_var = self.get_arrayconst_var(name, idxval)
			
			return 'Global', array_var
			
		if type == 'ArrayExpr':
			name, idx_expr = content
			
			if name not in self.environment.arrays:
				raise NameError('Tried to use undefined array "{}"'.format(name))
				
			index_var = '{}Idx'.format(name)
			id = idx_expr.compile(self, index_var)
			if id == None:
				raise Exception('Unable to calculate array "{}" index'.format(name))
			
			if id != index_var:
				self.add_command('scoreboard players operation Global {} = Global {}'.format(index_var, id))
				
			if initialize:
				self.add_command('function {}:array_{}_get'.format(self.namespace, name.lower()))
			
			self.free_scratch(id)
			
			return 'Global', '{}Val'.format(name)
		
		else:
			raise Exception('Tried to get unknown variable type "{}"'.format(type))

			
	def set_variable(self, variable):
		type, content = variable
		
		if type == 'Var':
			id, var = content
			self.set_path(id, var)
			
		elif type == 'ArrayExpr':
			name, idx_expr = content
			self.add_command('function {}:array_{}_set'.format(self.namespace, name.lower()))
	
	def get_arrayconst_var(self, name, idxval):
		return self.environment.get_arrayconst_var(name, idxval)

	def get_if_chain(self, conditions, iftype='if'):
		test = ''
		for type, val in conditions:
			if type == 'selector':
				test += '{0} entity {1} '.format(iftype, val)
			elif type == 'score':
				var, op, (rtype, rval) = val
				
				lselector, lvar = self.get_variable(var, initialize = True)
				
				if rtype == 'num':
					rval = self.apply_replacements(rval)
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
					rselector, rvar = self.get_variable(rval, initialize = True)
					
					self.register_objective(rvar)
					self.get_path(rselector, rvar)
					test += '{0} score {1} {2} {3} {4} {5} '.format(iftype, lselector, lvar, op, rselector, rvar)
				else:
					raise ValueError('Unknown if comparison type: "{}"'.format(rtype))
			elif type == 'pointer':
				var, rselector = val
				
				lselector, id = self.get_variable(var, initialize = True)
				
				self.register_objective(id)
				test += '{0} score {1} {2} = {3} _id '.format(iftype, lselector, id, rselector)
				
			elif type == 'vector_equality':
				if iftype == 'unless':
					raise ValueError('Vector equality may not  be used with "unless"')
				
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
						sel2, sco2 = var2[i]
					test += 'if score {} {} = {} {} '.format(sel1, sco1, sel2, sco2)
					
			elif type == 'block':
				relcoords, block = val
				block = self.apply_environment(block)
				
				if block in self.block_tags:
					block = '#{0}:{1}'.format(self.namespace, block)
				else:
					block = 'minecraft:{0}'.format(block)
					
				test += '{0} block {1} {2} '.format(iftype, ' '.join(relcoords), block)
			else:
				raise ValueError('Unknown "if" type: {0}'.format(type))
		
		return test
		
	def get_execute_command(self, exec_items, exec_func):	
		cmd = 'execute '
		as_count = 0
		for type, _ in exec_items:
			if type[:2] == 'As':
				as_count += 1
				
				if as_count >= 2:
					print('Execute chain may only contain a single "as" clause.')
					return None
		
		at_vector_count = 0
		
		for type, val in exec_items:
			if type == 'If':
				cmd += self.get_if_chain(val)
			if type == 'Unless':
				cmd += self.get_if_chain(val, 'unless')
			elif type == 'As':
				cmd += 'as {0} '.format(val)
				exec_func.update_self_selector(val)
			elif type == 'AsId':
				var, attype = val
				
				selector, id = self.get_variable(var, initialize = True)
				
				self.register_objective('_id')
				self.register_objective(id)
				
				self.add_command('scoreboard players operation Global _id = {0} {1}'.format(selector, id))
									
				cmd += 'as @e if score @s _id = Global _id '.format(selector, id)
				
				if attype != None:
					exec_func.update_self_selector('@' + attype)
				else:
					exec_func.update_self_selector('@s')
			elif type == 'AsCreate':
				if len(exec_items) > 1:
					print('"as create" may not be paired with other execute commands.')
					return None
				create_operation = val
					
				self.register_objective('_age')
				self.add_command('scoreboard players add @e _age 1')
				
				create_operation.compile(self)
					
				self.add_command('scoreboard players add @e _age 1')
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
					scale = self.scale

				vec_vals = expr.compile(self, None)
				self.add_command('scoreboard players add @e _age 1')
				self.add_command('summon area_effect_cloud')
				self.add_command('scoreboard players add @e _age 1')
				for i in range(3):
					self.add_command('execute store result entity @e[_age==1,limit=1] Pos[{0}] double {1} run scoreboard players get Global {2}'.format(i, 1/float(scale), vec_vals[i]))
				cmd += 'at @e[_age == 1] '
				exec_func.add_command('/kill @e[_age == 1]')
			elif type == 'In':
				dimension = val
				cmd += 'in {} '.format(dimension)
				
		return cmd
			
	def switch_cases(self, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
		for q in range(4):
			imin = q * len(cases) / 4
			imax = (q+1) * len(cases) / 4
			if imin == imax:
				continue
		
			vmin = cases[imin][0]
			vmax = cases[imax-1][1]
			line = cases[imin][3]
			
			sub_cases = cases[imin:imax]
			case_func = self.create_child_function()
			
			if len(sub_cases) == 1:
				vmin, vmax, sub, line, dollarid = sub_cases[0]
				if dollarid != None:
					case_func.set_dollarid(dollarid, vmin)
				try:
					case_func.compile_blocks(sub)
				except Exception as e:
					print(e.message)
					print('Unable to compile case at line {}'.format(line))
					return False
					
				single_command = case_func.single_command()
				if single_command != None:
					self.add_command('execute if score Global {} matches {}..{} run {}'.format(var, vmin, vmax, single_command))
				else:
					unique = self.get_unique_id()

					if vmin == vmax:
						case_name = '{}{}_{:03}_ln{}'.format(case_func_name, vmin, unique, line)
					else:
						case_name = '{}{}-{}_{:03}_ln{}'.format(case_func_name, vmin, vmax, unique, line)
						
					self.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, self.namespace, case_name))
					self.register_function(case_name, case_func)
			else:
				unique = self.get_unique_id()
				case_name = '{}{}-{}_{:03}_ln{}'.format(switch_func_name, vmin, vmax, unique, line)
				self.add_command('execute if score Global {} matches {}..{} run function {}:{}'.format(var, vmin, vmax, self.namespace, case_name))
				self.register_function(case_name, case_func)
			
				if not case_func.switch_cases(var, sub_cases):
					return False
			
		return True

		
	def add_operation(self, selector, id1, operation, id2):
		selector = self.environment.apply(selector)
		
		self.add_command("scoreboard players operation {0} {1} {2} {0} {3}".format(selector, id1, operation, id2))
			
		if self.is_scratch(id2):
			self.free_scratch(id2)
		
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
				self.register_objective("Param{0}".format(p))
			
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
			
		parsed = self.environment.get_selector_definition(selector)
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
				scale = self.scale
			
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
				scale = self.scale

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
				scale = self.scale

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
				scale = self.scale

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
			except:
				print('Error compiling block at line {}'.format(block.line))
				raise
					
	@property
	def parser(self):
		return self.environment.parser
		
	def import_file(self, filename):
		file = source_file(filename)
		result = self.parser('import ' + file.get_text() + '\n')
		if result == None:
			raise Exception('Unable to parse file "{}"'.format(filename))
		
		type, parsed = result
		if type != 'lib':
			raise Exception('Unable to import non-lib-file "{}"'.format(filename))
			
		self.compile_blocks(parsed['assignments'])
		
		for section in parsed['sections']:
			type, id, template_params, params, sub = section
			if type == 'macro':
				self.macros[id] = (params, sub)
			elif type == 'template_function':
				self.template_functions[id] = (template_params, params, sub)
				
		for section in parsed["sections"]:
			if section[0] == 'macro' or section[0] == 'template_function':
				continue
				
			compile_section(section, self.environment)
			