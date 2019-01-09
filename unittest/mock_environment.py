class mock_environment(object):
	def __init__(self):
		self.dollarid = {}
		self.functions = {}
		
	def clone(self):
		return mock_environment()
		
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