from .relcoord import relcoord
from .const_string import const_string

class relcoords(object):
	def __init__(self, coords = None):
		if coords == None:
			self.coords = (
				relcoord('~', const_string('')),
				relcoord('~', const_string('')),
				relcoord('~', const_string('')),
			)
		else:
			self.coords = coords
		
	def get_value(self, func):
		return ' '.join([c.get_value(func) for c in self.coords])