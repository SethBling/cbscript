from block_types.block_base import block_base
from variable_types.storage_path_var import storage_path_var

class push_block(block_base):
	def __init__(self, line, expr_list):
		self.expr_list = expr_list
		self.line = line
		
	def compile(self, func):
		func.add_command('data modify storage {} stack append value {{}}'.format(func.namespace))
	
		idx = 0
		for expr in self.expr_list:
			expr_var = expr.compile(func)
			data_var = storage_path_var(None, 'stack[-1].v{}'.format(idx))
			data_var.copy_from(func, expr_var)
			
			idx += 1
