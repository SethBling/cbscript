import copy
import math
from scratch_tracker import scratch_tracker
from selector_definition import selector_definition
from CompileError import CompileError

def isNumber(s):
	try:
		val = float(s)
		
		if math.isinf(val):
			return False
			
		if math.isnan(val):
			return False
		
		return True
	except Exception:
		return False
		
def isInt(s):
	try:
		if isinstance(s, basestring):
			if s == str(int(s)):
				return True
			return False
		else:
			int(s)
			return True
	except Exception:
		return False
		
		
class environment(object):
	def __init__(self, global_context):
		self.dollarid = {}
		self.global_context = global_context
		self.scratch = scratch_tracker(global_context)
		self.locals = []
		self.selectors = {}
		self.self_selector = None
		self.pointers = {}
		self.block_definitions = {}
		
	def clone(self, new_function_name = None):
		new_env = environment(self.global_context)
		
		for id in self.selectors:
			new_env.selectors[id] = self.selectors[id]
			
		for id in self.block_definitions:
			new_env.block_definitions[id] = self.block_definitions[id]
			
		for id in self.pointers:
			new_env.pointers[id] = self.pointers[id]
		
		new_env.dollarid = copy.deepcopy(self.dollarid)
		if new_function_name == None:
			new_env.scratch = self.scratch
			new_env.locals = self.locals
		else:
			new_env.scratch.prefix = self.global_context.get_scratch_prefix(new_function_name)
			
			
		new_env.self_selector = self.self_selector
		
		return new_env
		
	def register_local(self, local):
		if local not in self.locals:
			self.locals.append(local)
		
	def apply(self, text):
		text = self.apply_replacements(text)
		text = self.compile_selectors(text)
		
		return text
		
	def apply_replacements(self, text, overrides = {}):
		replacements = {}
		for k in self.dollarid:
			replacements[k] = self.dollarid[k]
		
		for k in overrides:
			replacements[k] = overrides[k]
	
		for identifier in reversed(sorted(replacements.keys())):
			if isInt(replacements[identifier]):
				text = str(text).replace('-$' + identifier, str(-int(replacements[identifier])))
			elif isNumber(replacements[identifier]):
				text = str(text).replace('-$' + identifier, str(-float(replacements[identifier])))
			text = str(text).replace('$' + identifier, str(replacements[identifier]))	
			
		if text == None:
			raise Exception('Applying replacements to "{}" returned None.'.format(text))
			
		return text
	
	def set_dollarid(self, id, val):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0] == '$':
			id = id[1:]
			
		self.dollarid[id] = val
		
	def get_dollarid(self, id):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0] == '$':
			id = id[1:]
			
		return self.dollarid[id]
		
	def copy_dollarid(self, id, copyid):
		negate = False
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0].startswith('$'):
			id = id[1:]
		
		if copyid.startswith('$'):
			copyid = copyid[1:]
			
		if copyid.startswith('-$'):
			copyid = copyid[2:]
			negate = True
			
		self.dollarid[id] = self.dollarid[copyid]
		if negate:
			if isInt(self.dollarid[id]):
				self.dollarid[id] = str(-int(self.dollarid[id]))
			elif isNumber(self.dollarid[id]):
				self.dollarid[id] = str(-float(self.dollarid[id]))
			else:
				raise CompileError('Unable to negate value of ${} when copying to ${}, it has non-numeric value "{}"'.format(copyid, id, self.dollarid[id]))
		
	def set_atid(self, id, fullselector):
		self.selectors[id] = selector_definition(fullselector, self)
		
		return self.selectors[id]
	
	def compile_selectors(self, command):
		ret = ""
		for fragment in self.split_selectors(command):
			if fragment[0] == "@":
				ret = ret + self.compile_selector(fragment)
			else:
				ret = ret + fragment
				
		return ret		
	
	def get_selector_parts(self, selector):
		if len(selector) == 2:
			selector += "[]"
		
		start = selector[0:3]
		end = selector[-1]
		middle = selector[3:-1]

		parts = middle.split(',')
		
		return start, [part.strip() for part in parts], end
		
	def compile_selector(self, selector):
		sel = selector_definition(selector, self)
		interpreted = sel.compile()
		
		if len(interpreted) == 4:
			# We have @a[] or similar, so truncate
			interpreted = interpreted[:2]
		
		return interpreted
		
	def get_python_env(self):
		return self.dollarid
		
	def register_objective(self, objective):
		if len(objective) > 16:
			raise CompileError('Objective name "{0}" is {1} characters long, max is 16.'.format(objective, len(objective)))
		self.global_context.register_objective(objective)
		
	def split_selectors(self, line):
		fragments = []
		
		remaining = str(line)
		while '@' in remaining:
			parts = remaining.split('@', 1)
			if len(parts[0]) > 0:
				fragments.append(parts[0])

			end = 0
			for i in range(len(parts[1])):
				if parts[1][i].isalnum() or parts[1][i] == '_':
					end += 1
				elif parts[1][i] == '[':
					brack_count = 1
					for j in range(i+1, len(parts[1])):
						if parts[1][j] == '[':
							brack_count += 1
						if parts[1][j] == ']':
							brack_count -= 1
						if brack_count == 0:
							end = j+1
							break
					break
				else:
					break
					
			fragments.append('@' + parts[1][:end])
			remaining = parts[1][end:]
						
		if len(remaining) > 0:
			fragments.append(remaining)
			
		#print(line, fragments)
		
		return fragments
		
	def update_self_selector(self, selector):
		if selector[0] != '@':
			return
			
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.selectors:
			self.self_selector = self.selectors[id]
			
	def register_objective(self, objective):
		self.global_context.register_objective(objective)
		
	def register_array(self, name, from_val, to_val, selector_based):
		self.global_context.register_array(name, from_val, to_val, selector_based)
		
	def register_block_tag(self, name, blocks):
		self.global_context.register_block_tag(name, blocks)
		
	def register_entity_tag(self, name, entities):
		self.global_context.register_entity_tag(name, entities)
	
	def register_item_tag(self, name, items):
		self.global_context.register_item_tag(name, items)
		
	def get_scale(self):
		return self.global_context.scale
		
	def set_scale(self, scale):
		self.global_context.scale = scale
		
	scale = property(get_scale, set_scale)
	
	@property
	def arrays(self):
		return self.global_context.arrays
	
	@property
	def block_tags(self):
		return self.global_context.block_tags

	@property
	def item_tags(self):
		return self.global_context.item_tags
		
	@property
	def entity_tags(self):
		return self.global_context.entity_tags
	
	@property
	def namespace(self):
		return self.global_context.namespace
	
	@property
	def macros(self):
		return self.global_context.macros
		
	@property
	def template_functions(self):
		return self.global_context.template_functions

	@property
	def functions(self):
		return self.global_context.functions
		
	def get_scratch(self):
		return self.scratch.get_scratch()
	
	def get_scratch_vector(self):
		return self.scratch.get_scratch_vector()
		
	def is_scratch(self, var):
		return self.scratch.is_scratch(var)
	
	def free_scratch(self, id):
		self.scratch.free_scratch(id)
		
	def get_temp_var(self):
		return self.scratch.get_temp_var()
		
	def free_temp_var(self):
		self.scratch.free_temp_var()
		
	def add_constant(self, val):
		return self.global_context.add_constant(val)
		
	def get_friendly_name(self):
		return self.global_context.get_friendly_name()
		
	def get_random_objective(self):
		return self.global_context.get_random_objective()
		
	def register_function(self, name, func):
		self.global_context.register_function(name, func)
	
	def get_unique_id(self):
		return self.global_context.get_unique_id()
		
	def register_clock(self, name):
		self.global_context.register_clock(name)
		
	def get_selector_definition(self, selector_text):
		if selector_text.startswith('@'):
			return selector_definition(selector_text, self)
		else:
			return None
		
	@property
	def parser(self):
		return self.global_context.parser

	def register_dependency(self, filename):
		self.global_context.register_dependency(filename)
		
	def add_pointer(self, block_id, selector):
		self.pointers[block_id] = selector
		
	def add_block_definition(self, block_id, definition):
		self.block_definitions[block_id] = definition
		
	def get_block_definition(self, block_id):
		if block_id not in self.block_definitions:
			raise CompileError('[{}] is not defined.'.format(block_id))
		
		return self.block_definitions[block_id]
		
	def get_block_path(self, func, block_id, path_id, coords, macro_args, initialize):
		if block_id not in self.block_definitions:
			raise CompileError('[{}] is not defined.'.format(block_id))
		
		if initialize:
			self.block_definitions[block_id].get_path(func, path_id, coords, macro_args)
		
		return 'Global', path_id
		
	def set_block_path(self, func, block_id, path_id, coords, macro_args, initialize):
		if block_id not in self.block_definitions:
			raise CompileError('[{}] is not defined.'.format(block_id))
		
		self.block_definitions[block_id].set_path(func, path_id, coords, macro_args)
		
	def add_recipe(self, recipe):
		self.global_context.add_recipe(recipe)
	
	def add_advancement(self, name, advancement):
		self.global_context.add_advancement(name, advancement)
		
	def add_loot_table(self, name, loot_table):
		self.global_context.add_loot_table(name, loot_table)
		
	def get_block_state_list(self):
		return self.global_context.get_block_state_list()
		
	def get_reset_function(self):
		return self.global_context.get_reset_function()