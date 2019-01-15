last_created = None

class mock_mcworld(object):
	def __init__(self, dir, namespace):
		self.dir = dir
		self.namespace = namespace
		self.functions = []
		self.clocks = []
		self.tags = []
		self.desc = None
		self.written = False		
	
	def write_functions(self, functions):
		self.functions += functions
		
	def write_tags(self, clocks, tags):
		self.clocks += clocks
		self.tags += tags
		
	def write_mcmeta(self, desc):
		self.desc = desc
		
	def write_zip(self):
		self.written = True