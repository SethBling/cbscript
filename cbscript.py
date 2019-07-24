import global_context
import mcworld
from environment import environment
from mcfunction import mcfunction, get_line, compile_section
from selector_definition import selector_definition
from source_file import source_file
from CompileError import CompileError
import tellraw
import traceback
import math
import collections
import time

class cbscript(object):
	def __init__(self, source_file, parse_func):
		self.source_file = source_file
		self.parse = parse_func
		self.namespace = self.source_file.get_base_name().split('.')[0].lower()
		self.dependencies = []
	
	def log(self, text):
		print(text)
		
	def log_traceback(self):
		traceback.print_exc()
	
	def check_for_update(self):
		recompile = False
		# It's important to go through all the files, to make sure that if multiple were updated
		# we don't try to compile multiple times
		for file in [self.source_file] + self.dependencies:
			if file.was_updated():
				recompile = True
				
		if recompile:
			self.try_to_compile()
	
	def try_to_compile(self):
		try:
			self.log('Compiling {0}...'.format(self.namespace))
			success = self.compile_all()
			if success:
				self.log("Script successfully applied at {}.".format(time.ctime()))
			else:
				self.log("Script had compile error(s).\a")
		except SyntaxError as e:
			self.log(str(e) + '\a')
		except CompileError as e:
			self.log(str(e) + '\a')
		except Exception as e:
			self.log("Compiler encountered unexpected error during compilation:\a")
			self.log_traceback()
		
	def create_world(self, dir, namespace):
		return mcworld.mcworld(dir, namespace)
	
	def compile_all(self):
		text = self.source_file.get_text()
	
		result = self.parse(text + "\n")
		
		if result == None:
			self.log('Unable to parse script.')
			return False
		
		type, parsed = result
		
		if type <> 'program':
			self.log('Script does not contain a full program.')
			return False
			
		self.global_context = global_context.global_context(self.namespace)
		global_environment = environment(self.global_context)
		global_func = mcfunction(global_environment)
		
		self.global_context.scale = parsed['scale']
		self.global_context.parser = self.parse

		try:
			global_func.compile_blocks(parsed['assignments'])
		except Exception as e:
			print(e)
			self.dependencies = [source_file(d) for d in self.global_context.dependencies]
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
				
			try:
				compile_section(section, global_environment)
			except CompileError as e:
				print(e)
				return False
			except:
				self.log_traceback()
				return False
		
		self.post_processing()
			
		world = self.create_world(parsed["dir"], self.namespace)

		world.write_functions(self.global_context.functions)
		world.write_tags(self.global_context.clocks, self.global_context.block_tags, self.global_context.item_tags)
		world.write_mcmeta(parsed['desc'])
		world.write_recipes(self.global_context.recipes)
		world.write_advancements(self.global_context.advancements)
		world.write_loot_tables(self.global_context.loot_tables)
		world.write_zip()
		
		self.dependencies = [source_file(d) for d in self.global_context.dependencies]
			
		return True
		
	def post_processing(self):
		self.global_context.finalize_functions()
		self.add_scratch_objectives()
		self.add_temp_objectives()
		self.add_constants()
		self.add_random_generation()
		self.add_trigger_objectives()
		self.add_registered_objectives()
		self.add_max_chain_length()
		
	def add_max_chain_length(self):
		f = self.global_context.get_reset_function()
		f.insert_command('/gamerule maxCommandChainLength 1000000000', 0)
		
	def add_scratch_objectives(self):
		f = self.global_context.get_reset_function()
		
		for prefix in self.global_context.scratch:			
			for i in xrange(self.global_context.scratch[prefix]):
				f.insert_command('/scoreboard objectives add {0}_scratch{1} dummy'.format(prefix, i), 0)
	
	
	def add_temp_objectives(self):
		f = self.global_context.get_reset_function()
		
		for t in xrange(self.global_context.temp):
			f.insert_command('scoreboard objectives add temp{0} dummy'.format(str(t)), 0)
	
	def add_constants(self):
		self.global_context.add_constant_definitions()
	
	def add_random_generation(self):
		f = self.global_context.get_reset_function()
		
		if self.global_context.rand > 0:
			objective = self.global_context.get_random_objective()
			commands = []
			commands.append('kill @e[type=armor_stand,name={0},scores={{{0}=0..}}]'.format(objective))
			commands.append("scoreboard objectives add {0} dummy".format(objective))
			for i in xrange(self.global_context.rand):
				commands.append('summon minecraft:armor_stand ~ ~ ~ {{CustomName:"\\"{0}\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}}'.format(objective))
				commands.append('scoreboard players add @e[type=armor_stand,name={0}] {0} 1'.format(objective))
			commands.append('scoreboard players remove @e[type=armor_stand,name={0}] {0} 1'.format(objective))	
			
			for i in range(len(commands)):
				f.insert_command(commands[i], i)
			
	def add_trigger_objectives(self):
		None
	
	def add_registered_objectives(self):
		reset = self.global_context.get_reset_function()
		
		defined = reset.defined_objectives()
		
		for objective in self.global_context.objectives.keys():
			if objective not in defined:
				reset.insert_command("/scoreboard objectives add {0} dummy".format(objective), 0)