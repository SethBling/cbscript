class mock_selector_definition(object):
	def __init__(self):
		self.scores_min = {}
		self.scores_max = {}
		self.parts = {}
		self.paths = {}
		self.vector_paths = {}
		
	def set_part(self, part, val):
		self.parts[part] = val