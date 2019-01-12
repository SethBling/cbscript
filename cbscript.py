import scriptparse
import global_context
import mcworld
from environment import environment
from mcfunction import mcfunction, get_line, compile_section
from selector_definition import selector_definition
import tellraw
import traceback
import math
import collections

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
			print "Compiler encountered unexpected error during compilation:\a"
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

		try:
			global_func.compile_blocks(parsed['assignments'])
		except:
			traceback.print_exc()
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
			except:
				traceback.print_exc()
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