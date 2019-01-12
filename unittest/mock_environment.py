class mock_environment(object):
	def __init__(self):
		self.dollarid = {}
		self.functions = {}
		self.self_selector = None
		
	def clone(self, new_function_name=None):
		env = mock_environment()
		env.function_name = new_function_name
		return env
		
	def apply(self, text):
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