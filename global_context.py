from mcfunction import mcfunction
from CompileError import CompileError

def get_friendly_name(namespace):
	name = "CB" + namespace[:14]
	name = name.replace(' ', '_')
	name = name.replace('.', '_')
	name = name.replace(',', '_')
	name = name.replace(':', '_')
	name = name.replace('{', '_')
	name = name.replace('}', '_')
	name = name.replace('=', '_')
	
	return name

def get_constant_name(c):
		if c == -1:
			return 'minus'
		elif c >= 0:
			return 'c{}'.format(c)
		else:
			return 'cm{}'.format(-c)
		
class global_context(object):
	def __init__(self, namespace):
		self.clocks = []
		self.functions = {}
		self.macros = {}
		self.template_functions = {}
		self.reset = None
		self.objectives = {}
		self.constants = []
		self.arrays = {}
		self.scratch = {}
		self.temp = 0
		self.rand = 0
		self.unique = 0
		self.friendly_name = get_friendly_name(namespace)
		self.block_tags = {}
		self.item_tags = {}
		self.scratch_prefixes = {}
		self.namespace = namespace
		self.parser = None
		self.dependencies = []
		self.recipes = []
		self.advancements = {}
		self.loot_tables = {}

	def register_block_tag(self, name, blocks):
		self.block_tags[name] = blocks
		
	def register_item_tag(self, name, items):
		self.item_tags[name] = items
		
	def get_unique_id(self):
		self.unique += 1
		return self.unique
	
	def register_clock(self, name):
		self.clocks.append(name)
		
	def register_function(self, name, func):
		self.functions[name] = func
		
	def register_array(self, name, from_val, to_val, selector_based):
		if name in self.arrays:
			raise CompileError('Array "{}" is defined multiple times.'.format(name))
		self.arrays[name] = (from_val, to_val, selector_based)
		
	def register_objective(self, objective):
		if len(objective) > 16:
			raise CompileError('Cannot create objective "{}", name is {} characters (max is 16)'.format(objective, len(objective)))
		self.objectives[objective] = True
	
	def get_reset_function(self):
		return self.functions['reset']
		
	def add_constant(self, c):
		try:
			c = int(c)
		except:
			print(e)
			raise Exception('Unable to create constant integer value for "{}"'.format(c))
			
		if c not in self.constants:
			self.constants.append(c)
	
		return get_constant_name(c)
		
	def add_constant_definitions(self):
		f = self.get_reset_function()
	
		if len(self.constants) > 0:
			f.insert_command('/scoreboard objectives add Constant dummy', 0)
			for c in self.constants:
				f.insert_command('/scoreboard players set {} Constant {}'.format(get_constant_name(c), c), 1)

	def allocate_scratch(self, prefix, n):
		if prefix not in self.scratch:
			self.scratch[prefix] = 0
			
		if n > self.scratch[prefix]:
			self.scratch[prefix] = n
	
	def allocate_temp(self, temp):
		if temp > self.temp:
			self.temp = temp
	
	def allocate_rand(self, rand):
		if rand > self.rand:
			self.rand = rand
	
	def finalize_functions(self):
		for func in self.functions.values():
			func.finalize()
			
	def get_scratch_prefix(self, name):
		name = name[:3]
		if name in self.scratch_prefixes:
			i = 2
			while '{0}{1}'.format(name, i) in self.scratch_prefixes:
				i += 1
			
			name = '{0}{1}'.format(name, i)
			self.scratch_prefixes[name] = True
			return name
		else:
			self.scratch_prefixes[name] = True
			return name

	def get_random_objective(self):
		return "RV" + self.friendly_name[2:]
		
	def register_dependency(self, filename):
		self.dependencies.append(filename)
		
	def add_recipe(self, recipe):
		self.recipes.append(recipe)
		
	def add_advancement(self, name, advancement):
		self.advancements[name] = advancement
		
	def add_loot_table(self, name, loot_table):
		self.loot_tables[name] = loot_table