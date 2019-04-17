class mock_environment(object):
	def __init__(self):
		self.dollarid = {}
		self.functions = {}
		self.self_selector = None
		self.selectors = {}
		self.objectives = []
		self.scratch = 0
		self.selector_definitions = {}
		self.arrays = {}
		self.block_tags = {}
		self.scale = 1000
		self.cloned_environments = []
		self.applied = []
		self.copied_dollarids = []
		
	def clone(self, new_function_name=None):
		env = mock_environment()
		env.function_name = new_function_name
		self.cloned_environments.append(env)
		return env
		
	def apply(self, text):
		self.applied.append(text)
		
		return text
		
	def get_unique_id(self):
		return 1
		
	@property
	def namespace(self):
		return 'test_namespace'
		
	def register_function(self, name, func):
		self.functions[name] = func
		
	def set_dollarid(self, id, val):
		self.dollarid[id] = val
		
	def update_self_selector(self, selector):
		self.self_selector = selector
		
	def register_local(self, var):
		None
		
	def apply_replacements(self, text):
		return text
		
	def register_objective(self, objective):
		self.objectives.append(objective)
		
	def is_scratch(self, id):
		return 'scratch' in id
		
	def get_scratch(self):
		self.scratch += 1
		return 'test_scratch{}'.format(self.scratch)
		
	def free_scratch(self, id):
		None
		
	def get_selector_definition(self, selector_text):
		return self.selector_definitions[selector_text]
	
	def get_arrayconst_var(self, name, idxval):
		return '{}{}'.format(name, idxval)
		
	def copy_dollarid(self, id1, id2):
		self.dollarid[id1] = self.dollarid[id2]
		
	def get_python_env(self):
		return self.dollarid