from environment import isNumber, isInt

class const_number(object):
	def __init__(self, val):
		if not isNumber(val):
			raise Exception(f'Non-numeric value "{val}" for number.')
		if isInt(val):
			self.val = int(val)
		else:
			self.val = float(val)
		
	def get_value(self, func):
		return self.val
