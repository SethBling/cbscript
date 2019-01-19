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
		self.scratch = 0
		self.cloned_environments = []
		self.environment_pushes = 0
		self.environment_pops = 0
		self.constants = {}
		self.finalized = False
		self.temp = 0
		self.switch_calls = []
		self.execute_command_calls = []
		self.set_var = {}
		self.self_selector = None
		
	def add_operation(self, selector, id1, operation, id2):
		self.add_command("scoreboard players operation {0} {1} {2} {0} {3}".format(selector, id1, operation, id2))
		
	def add_command(self, command):
		self.commands.append(command)
	
	def insert_command(self, command, index):
		self.commands.insert(index, command)
		
	def get_utf8_text(self):
		return ''
		
	def defined_objectives(self):
		return {}
		
	def register_local(self, id):
		None
			
	def finalize(self):
		self.finalized = True
		
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
		self.scratch += 1
		return 'test_scratch{}'.format(self.scratch)
		
	def free_scratch(self, id):
		None
		
	def apply_environment(self, text):
		return text
		
	def add_constant(self, val):
		self.constants[val] = True
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
		self.self_selector = selector
		
	def get_python_env(self):
		return {}
		
	def clone_environment(self):
		env = mock_environment()
		self.cloned_environments.append(env)
		return env
		
	def get_combined_selector(self, selector):
		return mock_selector_definition()
		
	def set_dollarid(self, id, val):
		self.dollarid[id] = val
		
	def set_atid(self, id, fullselector):
		self.selectors[id] = mock_selector_definition()
		self.selectors[id].selector = fullselector
		
		return self.selectors[id]
		
	def push_environment(self, new_env):
		self.environment_pushes += 1
		
	def pop_environment(self):
		self.environment_pops += 1
		
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
		self.temp += 1
		return 'temp{}'.format(self.temp)
		
	def free_temp_var(self, var):
		None
		
	def switch_cases(self, var, cases, switch_func_name = 'switch', case_func_name = 'case'):
		self.switch_calls.append((var, cases, switch_func_name, case_func_name))
		
		return True
		
	def get_execute_command(self, exec_items, exec_func):
		self.execute_command_calls.append(exec_items)
		
		return 'execute_dummy '
		
	def get_variable(self, variable, initialize):
		self.scratch += 1
		return ('Global', 'var{}'.format(self.scratch))
		
	def set_variable(self, variable):
		self.set_var[variable] = True
		
	def get_arrayconst_var(self, name, idxval):
		return '{}{}'.format(name, idxval)
		
	def get_modifiable_id(self, id, assignto):
		if assignto != None:
			if id != assignto:
				self.add_operation('Global', assignto, '=', id)
				id = assignto
			else:
				return id
		else:
			newId = self.get_scratch()
			self.add_operation('Global', newId, '=', id)
			id = newId
			
			return id
			
	def evaluate_params(self, params):
		return True