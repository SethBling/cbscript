class block_nbt_path(object):
	def __init__(self, coords, path):
		self.coords = coords
		self.path = path
		
	def get_dest_path(self, func):
		return 'block {} {}'.format(self.coords.get_value(func), self.path)
		
	def get_source_path(self, func):
		return 'from ' + self.get_dest_path(func)