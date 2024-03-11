class mock_global_context(object):
	def __init__(self):
		self.temp = 0
		self.scratch = {}
		

	def allocate_temp(self, size):
		self.temp = size
		
	def allocate_scratch(self, prefix, size):
		self.scratch[prefix] = size
		
	def get_scratch_prefix(self, name):
		return f'{name}_prefix'
