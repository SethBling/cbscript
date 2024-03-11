from selector_definition import selector_definition
from environment import isNumber
from source_file import source_file
from variable_types.scoreboard_var import scoreboard_var
from block_types.push_block import push_block
from block_types.pop_block import pop_block
from CompileError import CompileError
import math
import traceback
import json

def get_undecorated_selector_name(selector):
	if selector.startswith('@'):
		selector = selector[1:]
	selector = selector.split('[')[0]
	
	return selector

def compile_section(section, environment):
	type, name, template_params, params, lines = section

	if type == 'function':
		f = mcfunction(environment.clone(new_function_name = name), True, params)
	elif type == 'reset':
		f = environment.get_reset_function()
		if f == None:
			f = mcfunction(environment.clone(new_function_name = name))
	else:
		f = mcfunction(environment.clone(new_function_name = name))
		
	environment.register_function(name, f)

	if type == 'clock':
		environment.register_clock(name)
		
	f.compile_blocks(lines)

def real_command(cmd):
		return not cmd.startswith('#') and len(cmd) > 0
	
class mcfunction(object):
	def __init__(self, environment, callable = False, params = []):
		self.commands = []
		self.environment = environment
		self.params = params
		self.callable = callable
		self.environment_stack = []
		self.has_macros = False
		self.filename = None
		
		for param in params:
			self.register_local(param)

	def set_filename(self, filename):
		self.filename = filename

	# Returns the command to call this function
	def get_call(self):
		if self.filename == None:
			raise CompileError('Tried to call function with no registered filename.')
		
		if self.has_macros:
			return f'function {self.namespace}:{self.filename} with storage {self.namespace}:global args'
		else:
			return f'function {self.namespace}:{self.filename}'

	def evaluate_params(self, params):
		results = []
		for p in range(len(params)):
			param_name = f'Param{p}'
			param_var = scoreboard_var('Global', param_name)
			try:
				var = params[p].compile(self, None)
			except Exception as e:
				print(e)
				print(f'Unable to compile parameter {p}.')
				return False
				
			param_var.copy_from(self, var)
		
		return True			

	def get_arrayconst_var(self, name, idxval):
		return self.environment.get_arrayconst_var(name, idxval)

	def get_if_chain(self, conditions, iftype='if'):
		test = ''
		for type, val in conditions:
			if type == 'selector':
				test += f'{iftype} entity {val} '
			elif type == 'predicate':
				if ':' in val:
					test += f'{iftype} predicate {val} '
				elif val in self.predicates:
					test += f'{iftype} predicate {self.namespace}:{val} '
				else:
					raise CompileError(f'Predicate "{val}" does not exist')
			elif type == 'score':
				lexpr, op, rexpr = val
				
				lvar = lexpr.compile(self)
				rvar = rexpr.compile(self)
				
				lconst = lvar.get_const_value(self)
				rconst = rvar.get_const_value(self)
				
				if lconst != None and rconst != None:
					result = False
					# Perform comparison, terminate if-chain if false
					if op == '=' and lconst == rconst:
						result = True
					elif op == '>' and lconst > rconst:
						result = True
					elif op == '<' and lconst < rconst:
						result = True
					elif op == '>=' and lconst >= rconst:
						result = True
					elif op == '<=' and lconst <= rconst:
						result = True
						
					if iftype == 'if' and not result or iftype == 'unless' and result:
						# Clobber entire if chain
						return 'if score Global unique matches -1 '
					else:
						# No modification to the test string is necessary
						continue
					
				elif lconst != None or rconst != None:
					# Continue if chain comparing the scoreboard value with numeric range
					if lconst != None:
						sbvar = rvar.get_scoreboard_var(self)
						const = lconst
					elif rconst != None:
						sbvar = lvar.get_scoreboard_var(self)
						const = rconst
						
					if op == '>':						
						test += f'{iftype} score {sbvar.selector} {sbvar.objective} matches {int(const)+1}.. '
					if op == '>=':						
						test += f'{iftype} score {sbvar.selector} {sbvar.objective} matches {const}.. '
					if op == '<':						
						test += f'{iftype} score {sbvar.selector} {sbvar.objective} matches ..{int(const)-1} '
					if op == '<=':						
						test += f'{iftype} score {sbvar.selector} {sbvar.objective} matches ..{const} '
					if op == '=':						
						test += f'{iftype} score {sbvar.selector} {sbvar.objective} matches {const} '
					
				else:
					# Continue if chain comparing two score values
					lsbvar = lvar.get_scoreboard_var(self)
					rsbvar = rvar.get_scoreboard_var(self)
					
					test += f'{iftype} score {lsbvar.selector} {lsbvar.objective} {op} {rsbvar.selector} {rsbvar.objective} '
				
			elif type == 'vector_equality':
				if iftype == 'unless':
					raise CompileError('Vector equality may not be used with "unless"')
				
				(type1, var1), (type2, var2) = val
				
				if type1 == 'VAR_CONST' and type2 == 'VAR_CONST':
					val1 = var1.get_value(self)
					val2 = var2.get_value(self)
					if val1 != val2:
						# Test fails, clobber entire chain
						return 'if score Global unique matches -1 '
					else:
						# Test succeeds, continue with the chain
						continue
				else:
					if type1 == 'VAR_CONST':
						# Swap vars so that the constant var is always second
						temp_type = type1
						temp_var = var1
						type1 = type2
						var1 = var2
						type2 = temp_type
						var2 = temp_var
						
					const_vals = []
					if type2 == 'VAR_CONST':
						components = var2.get_value(self)
						try:
							const_vals = [int(components[i]) for i in range(3)]
						except Exception as e:
							print(e)
							raise CompileError('Unable to get three components for constant vector.')
						
					for i in range(3):
						if type1 == 'VAR_ID':
							lvar = scoreboard_var('Global', f'_{var1}_{i}')
						elif type1 == 'SEL_VAR_ID':
							sel1, selvar1 = var1
							lvar = scoreboard_var(sel1, f'_{selvar1}_{i}')
						elif type1 == 'VAR_COMPONENTS':
							lvar = var1[i].get_scoreboard_var(self)
						
						if type2 == 'VAR_CONST':
							test += f'if score {sel1} {sco1} matches {const_vals[i]} '
						else:
							if type2 == 'VAR_ID':
								rvar = scoreboard_var('Global', f'_{var2}_{i}')
							elif type2 == 'SEL_VAR_ID':
								sel2, selvar2 = var2
								rvar = scoreboard_var(sel2, f'_{selvar2}_{i}')
							elif type2 == 'VAR_COMPONENTS':
								rvar = var2[i].get_scoreboard_var(self)
								
						test += f'if score {lvar.selvar} = {rvar.selvar} '
					
			elif type == 'block':
				relcoords, block = val
				block = self.apply_environment(block)
				
				if block in self.block_tags:
					block = f'#{self.namespace}:{block}'
				else:
					block = f'minecraft:{block}'
					
				test += f'{iftype} block {relcoords.get_value(self)} {block} '
			elif type == 'nbt_path':
				test += f'{iftype} data {val.get_dest_path(self)} '
			else:
				raise ValueError(f'Unknown "if" type: {type}')
		
		return test
		
	def get_execute_items(self, exec_items, exec_func):	
		cmd = ''
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
				cmd += f'as {val} '
				exec_func.update_self_selector(val)
			elif type == 'On':
				cmd += f'on {val} '
				exec_func.update_self_selector("@s")
			elif type == 'AsId':
				var, attype = val
				
				sbvar = var.get_scoreboard_var(self)
				selector, id = sbvar.selector, sbvar.objective
				
				if attype == None:
					psel = '@e'
				else:
					psel = f'@{attype}'
				if selector[0] == '@':
					seldef = selector_definition(selector, self.environment)
					if seldef.base_name == 's' and self.environment.self_selector != None and id in self.environment.self_selector.pointers:
						psel = self.environment.self_selector.pointers[id]
					elif id in seldef.pointers:
						psel = seldef.pointers[id]
				elif selector == 'Global':
					if id in self.environment.pointers:
						psel = self.environment.pointers[id]
				
				self.register_objective('_id')
				self.register_objective(id)
				
				self.add_command(f'scoreboard players operation Global _id = {selector} {id}')
									
				cmd += f'as {psel} if score @s _id = Global _id '
				
				if attype != None:
					exec_func.update_self_selector('@' + attype)
				elif psel != '@e':
					exec_func.update_self_selector('@' + get_undecorated_selector_name(psel))
				else:
					exec_func.update_self_selector('@s')
			elif type == 'AsCreate':
				if len(exec_items) > 1:
					print('"as create" may not be paired with other execute commands.')
					return None
				create_operation = val
					
				self.register_objective('_age')
				self.add_command(f'scoreboard players set @{create_operation.atid} _age 1')
				
				create_operation.compile(self)
					
				self.add_command(f'scoreboard players add @{create_operation.atid} _age 1')
				cmd += f'as @{create_operation.atid}[_age==1,limit=1] '
				
				exec_func.update_self_selector('@'+create_operation.atid)
			elif type == 'Rotated':
				cmd += f'rotated as {val} '
			elif type == 'FacingCoords':
				cmd += f'facing {val.get_value(self)} '
			elif type == 'FacingEntity':
				cmd += f'facing entity {val} feet '
			elif type == 'Align':
				cmd += f'align {val} '
			elif type == 'At':
				selector, relcoords, anchor = val
				if selector != None:
					cmd += f'at {selector} '
				if anchor != None:
					cmd += f'anchored {anchor} '
				if relcoords != None:
					cmd += f'positioned {relcoords.get_value(self)} '
			elif type == 'AtVector':
				at_vector_count += 1
				if at_vector_count >= 2:
					print('Tried to execute at multiple vector locations.')
					return None
					
				scale, expr = val
				if scale == None:
					scale = self.scale
				else:
					scale = scale.get_value(self)

				vec_vals = expr.compile(self, None)
				self.add_command('scoreboard players add @e _age 1')
				self.add_command('summon area_effect_cloud')
				self.add_command('scoreboard players add @e _age 1')
				for i in range(3):
					var = vec_vals[i].get_scoreboard_var(self)
					self.add_command(f'execute store result entity @e[_age==1,limit=1] Pos[{i}] double {1/float(scale)} run scoreboard players get {var.selector} {var.objective}')
				cmd += 'at @e[_age == 1] '
				exec_func.add_command('/kill @e[_age == 1]')
			elif type == 'In':
				dimension = val
				cmd += f'in {dimension} '
				
		return cmd
			
	def switch_cases(self, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
		for q in range(4):
			imin = q * len(cases) // 4
			imax = (q+1) * len(cases) // 4
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
				except CompileError as e:
					print(e)
					raise CompileError(f'Unable to compile case at line {line}')
				except Exception as e:
					print(traceback.format_exc())
					raise CompileError(f'Unable to compile case at line {line}')
					
				single_command = case_func.single_command()
				if single_command != None:
					if vmin == vmax:
						vrange = str(vmin)
					else:
						vrange = f'{vmin}..{vmax}'
						
					if len(single_command) >= 1 and single_command[0] == '$':
						self.add_command(f'$execute if score {var.selector} {var.objective} matches {vrange} run {single_command[1:]}')
					else:
						self.add_command(f'execute if score {var.selector} {var.objective} matches {vrange} run {single_command}')
				else:
					unique = self.get_unique_id()

					if vmin == vmax:
						case_name = f'line{line}/{case_func_name}{vmin}_{unique}'
					else:
						case_name = f'line{line}/{case_func_name}{vmin}-{vmax}_{unique}'
						
					self.register_function(case_name, case_func)
					self.add_command(f'execute if score {var.selector} {var.objective} matches {vmin}..{vmax} run {case_func.get_call()}')
			else:
				unique = self.get_unique_id()
				case_name = f'line{line}/{switch_func_name}{vmin}-{vmax}_{unique}'
				self.register_function(case_name, case_func)
				self.add_command(f'execute if score {var.selector} {var.objective} matches {vmin}..{vmax} run {case_func.get_call()}')
			
				if not case_func.switch_cases(var, sub_cases):
					return False
			
		return True

		
	def add_operation(self, selector, id1, operation, id2):
		selector = self.environment.apply(selector)
		
		self.add_command(f"scoreboard players operation {selector} {id1} {operation} {selector} {id2}")
			
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

			if '$(' in command:
				if command[0] != '$':
					command = '$' + command

				self.has_macros = True
				
			
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
				self.insert_command(f'scoreboard players operation Global {self.params[p]} = Global Param{p}', 0)
				self.register_objective(f"Param{p}")
			
		self.commands = comments + self.commands
		
	def single_command(self):
		ret = None
		count = 0
		for cmd in self.commands:
			if real_command(cmd):
				ret = cmd
				count += 1
			
			if count >= 2:
				return None
				
		return ret
		
	def is_empty(self):
		for cmd in self.commands:
			if real_command(cmd):
				return False
				
		return True
			
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
				raise CompileError(f'Tried to get data "{var}" from selector "{selector}" which is not limited to a single entity.')
				
			self.add_command(f'execute store result score {selector} {var} run data get entity {selector} {path} {scale}')
				
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
				raise CompileError(f'Tried to set data "{var}" for selector "{selector}" which is not limited to a single entity.')
				
			self.add_command(f'execute store result entity {selector} {path} {data_type} {1/float(scale)} run scoreboard players get {selector} {var}')

	def get_vector_path(self, selector, var):
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
				raise CompileError(f'Tried to get vector data "{var}" from selector "{selector}" which is not limited to a single entity.')
				
			for i in range(3):
				self.add_command(f'execute store result score {selector} _{var}_{i} run data get entity {selector} {path}[{i}] {scale}')
			
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
				raise CompileError(f'Tried to set vector data "{var}" for selector "{selector}" which is not limited to a single entity.')
				
			for i in range(3):
				val_var = values[i].get_scoreboard_var(self)
				self.add_command(f'execute store result entity {selector} {path}[{i}] {data_type} {1/float(scale)} run scoreboard players get {val_var.selector} {val_var.objective}')
			
			return True
		else:
			return False
			
	def register_objective(self, objective):
		self.environment.register_objective(objective)
		
	def register_array(self, name, from_val, to_val, selector_based):
		self.environment.register_array(name, from_val, to_val, selector_based)
		
	def apply_replacements(self, text, overrides = {}):
		return self.environment.apply_replacements(text, overrides)
		
	def register_block_tag(self, name, blocks):
		self.environment.register_block_tag(name, blocks)
	
	def register_entity_tag(self, name, entities):
		self.environment.register_entity_tag(name, entities)
		
	def register_item_tag(self, name, items):
		self.environment.register_item_tag(name, items)
		
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
	def item_tags(self):
		return self.environment.item_tags

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
		
	def get_self_selector_definition(self):
		return self.environment.self_selector
		
	def get_python_env(self):
		return self.environment.get_python_env()
		
	def clone_environment(self, new_function_name = None):
		return self.environment.clone(new_function_name = new_function_name)
		
	# Combines a selector with an existing selector definition in the environment
	def get_combined_selector(self, selector):
		return selector_definition(selector, self.environment)
		
	def set_dollarid(self, id, val):
		self.environment.set_dollarid(id, val)
		
	def get_dollarid(self, id):
		return self.environment.get_dollarid(id)
		
	def set_atid(self, id, fullselector):
		return self.environment.set_atid(id, fullselector)
		
	def push_environment(self, new_env):
		self.environment_stack.append(self.environment)
		self.environment = new_env
		
	def pop_environment(self):
		self.environment = self.environment_stack.pop()
		
	def run_create(self, atid, relcoords, idx=None):
		if atid not in self.selectors:
			print(f'Unable to create unknown entity: @{atid}')
			return False
		
		selector = self.selectors[atid]
		
		entity_type = selector.get_type()
		
		if entity_type == None:
			print(f'Unable to create @{atid}, no entity type is defined.')
			return False
			
		if selector.tag == None:
			if idx:
				self.add_command(f'summon {entity_type} {relcoords.get_value(self)} {idx.get_value(self) + hash(atid) % (2 ** 32)}}}')
			else:
				self.add_command(f'summon {entity_type} {relcoords.get_value(self)}')
		else:
			if idx:
				parsed = json.loads(selector.tag)
				parsed['UUIDMost'] = 0
				parsed['UUIDLeast'] = idx.get_value(self) + hash(atid) % (2 ** 32)
				tag = json.dumps(parsed)
			else:
				tag = selector.tag
			
			self.add_command(f'summon {entity_type} {relcoords.get_value(self)} {tag}')
			
		return True
	
	def register_name_definition(self, id, str):
		self.environment.register_name_definition(id, str)

	def get_name_definition(self, id):
		return self.environment.get_name_definition(id)
		
	# Creates an empty function with a copy of the current environment
	def create_child_function(self, new_function_name = None, callable = False, params = []):
		return mcfunction(self.clone_environment(new_function_name = new_function_name),
			callable = callable,
			params = params
		)

	def compile_blocks(self, lines):
		for block in lines:
			try:
				block.compile(self)
			except CompileError as e:
				print(e)
				raise CompileError(f'Error compiling block at line {block.line}')
			except:
				print(traceback.format_exc())
				raise CompileError(f'Error compiling block at line {block.line}')
					
	@property
	def parser(self):
		return self.environment.parser
		
	def import_file(self, filename):
		self.environment.register_dependency(filename)

		file = source_file(filename)
		
		result = self.parser('import ' + file.get_text() + '\n')
		if result == None:
			raise CompileError(f'Unable to parse file "{filename}"')
		
		type, parsed = result
		if type != 'lib':
			raise CompileError(f'Unable to import non-lib-file "{filename}"')
			
		for line in parsed['lines']:
			line.register(self.global_context)
			
		self.compile_blocks(parsed['lines'])
		
	def import_python_file(self, filename):
		self.environment.register_dependency(filename)
		
		try:
			with open(filename, 'rb') as file:
				text = file.read().decode('utf-8')
		except Exception as e:
			print(e)
			raise CompileError(f'Unable to open "{filename}"')
			
		try:
			exec(text, globals(), self.get_python_env())
		except Exception as e:
			print(e)
			raise CompileError(f'Unable to execute "{filename}"')
			
	def eval(self, expr, line):
		try:
			return eval(expr, globals(), self.get_python_env())
		except Exception as e:
			print(e)
			raise CompileError(f'Could not evaluate python expression "{expr}" at line {line}')
			
	def add_pointer(self, id, selector):
		self.environment.add_pointer(id, selector)
		
	def add_block_definition(self, id, definition):
		self.environment.add_block_definition(id, definition)
		
	def get_block_definition(self, block_id):
		return self.environment.get_block_definition(block_id)
		
	def get_selector_definition(self, selector):
		return self.environment.get_selector_definition(selector)
		
	def add_recipe(self, recipe):
		self.environment.add_recipe(recipe)
		
	def add_advancement(self, name, advancement):
		self.environment.add_advancement(name, advancement)
		
	def add_loot_table(self, name, loot_table):
		self.environment.add_loot_table(name, loot_table)
		
	def add_predicate(self, name, predicate):
		self.environment.add_predicate(name, predicate)
		
	def get_block_state_list(self, include_block_states):
		return self.environment.get_block_state_list(include_block_states)
		
	def call_function(self, sub_func, sub_name, prefix = ''):
		if sub_func.is_empty():
			return
	
		single_command = sub_func.single_command()
		
		if single_command:
			if single_command.startswith('$'):
				self.add_command(f'${prefix}{single_command[1:]}')
			else:
				self.add_command(f'{prefix}{single_command}')
		else:
			unique = self.get_unique_id()
			sub_name = f'{sub_name}_{unique}'
			
			self.register_function(sub_name, sub_func)
			cmd = prefix + sub_func.get_call()
				
			self.add_command(cmd)
			
	def get_reset_function(self):
		return self.environment.get_reset_function()
		
	def register_clock(self, id):
		self.environment.register_clock(id)
		
	@property
	def global_context(self):
		return self.environment.global_context
		
	def copy_environment_from(self, func):
		self.environment = func.environment.clone()
		
	@property
	def name(self):
		return self.environment.function_name
		
	def get_local_variables(self):
		return [scoreboard_var('Global', l) for l in self.environment.get_all_locals()]
		
	def push_locals(self, locals):
		block = push_block(0, locals)
		block.compile(self)
		
	def pop_locals(self, locals):
		block = pop_block(0, locals)
		block.compile(self)
		
	@property
	def predicates(self):
		return self.environment.predicates