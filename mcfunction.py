from selector_definition import selector_definition

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
		
		self.add_command("/scoreboard players operation {0} {1} {2} {0} {3}".format(selector, id1, operation, id2))
			
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
				self.insert_command('/scoreboard players operation Global {0} = Global Param{1}'.format(self.params[p], p), 0)
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
		self.environment.apply_replacements(text)
		
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
		
	def free_scratch(self, id):
		self.environment.free_scratch(id)
		
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
		self.environment.set_atid(id, fullselector)
		
	def push_environment(self, new_env):
		self.environment_stack.append(self.environment)
		self.environment = new_env
		
	def pop_environment(self):
		self.environment = self.environment_stack.pop()