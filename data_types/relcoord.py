class relcoord(object):
	def __init__(self, type, coord):
		self.type = type
		self.coord = coord
		
	def get_value(self, func):
		return self.type + str(self.coord.get_value(func))