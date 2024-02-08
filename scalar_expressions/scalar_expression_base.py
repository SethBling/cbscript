class scalar_expression_base(object):
	def const_value(self, func=None):
		return None
	
	# Returns true if this varariable/expression references the specified scoreboard variable
	def references_scoreboard_var(self, func, var):
		return False
