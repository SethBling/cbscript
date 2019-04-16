class const_string(object):
	def __init__(self, val):
		self.val = val
		
	def get_value(self, func):
		return self.val