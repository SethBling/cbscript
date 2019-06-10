from variable_types.virtualint_var import virtualint_var
from CompileError import CompileError

class vector_var_const_vector(object):
	def __init__(self, value):
		self.value = value
		
	def compile(self, func, assignto):
		components = self.value.get_value(func)
		
		vars = []
		try:
			vars = [virtualint_var(int(components[i])) for i in range(3)]
		except Exception as e:
			print(e)
			raise CompileError('Unable to get three components from constant vector expression.')
				
		return vars
