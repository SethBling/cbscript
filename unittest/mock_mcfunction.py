from mock_environment import mock_environment
from mock_selector_definition import mock_selector_definition

class mock_mcfunction(object):
	def __init__(self):
		self.commands = []
		self.dollarid = {}
		self.atid = {}
		self.macros = {}
		self.template_functions = {}
		self.arrays = {}
		self.block_tags = {}
		self.namespace = 'test_namespace'
		self.functions = {}
		self.selectors = {}
		self.child_functions = []
		self.created = []
		self.compiled_blocks = []
		self.operations = []
		
	def add_operation(self, selector, id1, operation, id2):
		self.operations.append((selector, id1, operation, id2))
		
	def add_command(self, command):
		self.commands.append(command)
	
	def insert_command(self, command, index):
		None
		
	def get_utf8_text(self):
		return ''
		
	def defined_objectives(self):
		return {}
		
	def register_local(self, id):
		None
			
	def finalize(self):
		None
		
	def single_command(self):
		return None
			
	def check_single_entity(self, selector):
		return False
			
	def get_path(self, selector, var):
		None
				
	def set_path(self, selector, var):
		None

	def get_vector_path(self, selector, var, assignto):
		return False
			
	def set_vector_path(self, selector, var, values):
		return True
			
	def register_objective(self, objective):
		None
		
	def register_array(self, name, from_val, to_val):
		self.arrays[name] = (from_val, to_val)

	def apply_replacements(self, text):
		return text
		
	def register_block_tag(self, name, blocks):
		self.block_tags[name] = blocks
		
	def get_scale(self):
		return 1000
		
	def set_scale(self, scale):
		None
		
	scale = property(get_scale, set_scale)
	
	def get_scratch(self):
		return 'test_scratch'
		
	def free_scratch(self, id):
		None
		
	def apply_environment(self, text):
		return text
		
	def add_constant(self, val):
		return 'test_constant'
		
	def allocate_rand(self, val):
		None
		
	def get_friendly_name(self):
		return 'test_friendly_name'
		
	def get_random_objective(self):
		return 'test_random_objective'
		
	def register_function(self, name, func):
		self.functions[name] = func
		
	def get_unique_id(self):
		return 1
		
	def update_self_selector(self, selector):
		None
		
	def get_python_env(self):
		return {}
		
	def clone_environment(self):
		return mock_environment()
		
	def get_combined_selector(self, selector):
		return mock_selector_definition()
		
	def set_dollarid(self, id, val):
		self.dollarid[id] = val
		
	def set_atid(self, id, fullselector):
		self.atid[id] = fullselector
		
		return mock_selector_definition()
		
	def push_environment(self, new_env):
		None
		
	def pop_environment(self):
		None		
		
	def run_create(self, atid, relcoords):
		self.created.append((atid, relcoords))
		return True
		
	def perform_execute(self, type, line_num, exec_items, sub):
		return True
		
	def create_child_function(self):
		child = mock_mcfunction()
		self.child_functions.append(child)
		return child
		
	def compile_blocks(self, lines):
		self.compiled_blocks.append(lines)
		return True
		
	def is_scratch(self, var):
		return False
		
	def get_temp_var(self):
		return 'test_temp_var'