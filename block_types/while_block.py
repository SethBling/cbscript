from execute_base import execute_base
from mcfunction import get_execute_command

class while_block(execute_base):
	def __init__(self, line, exec_items, sub):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		
	def compile(self, func):
		self.perform_execute(func)
		
	# Force a sub-function for the continuation commands
	def force_sub_function(self):
		return True
		
	def add_continuation_command(self, func_name, exec_func):
		dummy_func = exec_func.create_child_function()
		sub_cmd = get_execute_command(self.exec_items, exec_func, dummy_func)
		if sub_cmd == None:
			raise Exception('Unable to compile continuation command for while block at line {}'.format(self.line))

		exec_func.add_command('{0}run function {1}:{2}'.format(sub_cmd, exec_func.namespace, func_name))
		
	def display_name(self):
		return 'while'