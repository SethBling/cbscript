from .block_base import block_base
from variable_types.storage_path_var import storage_path_var

class pop_block(block_base):
	def __init__(self, line, var_list):
		self.var_list = var_list
		self.line = line
		
	def compile(self, func):
		idx = 0
		for var in self.var_list:
			data_var = storage_path_var(None, f'stack[-1].v{idx}')
			var.copy_from(func, data_var)
			
			idx += 1
			
		func.add_command(f'data remove storage {func.namespace} stack[-1]')
