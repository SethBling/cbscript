import traceback
from CompileError import CompileError

class execute_base(object):
	# Override to force the creation of a sub function, even for a single command
	def force_sub_function(self):
		return False
		
	# By default, no continuation is added to the end of the sub function
	def add_continuation_command(self, func, func_name, exec_func):
		None
		
	def prepare_scratch(self, func):
		None

	def perform_execute(self, func):
		self.prepare_scratch(func)
		exec_func = func.create_child_function()
		
		cmd = func.get_execute_command(self.exec_items, exec_func)
		if cmd == None:
			raise CompileError('Unable to compile {0} block at line {1}'.format(self.display_name(), self.line))
		
		try:
			exec_func.compile_blocks(self.sub)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile {} block contents at line {}'.format(self.display_name(), self.line))
		except Exception as e:
			print(traceback.format_exc())
			raise CompileError('Unable to compile {} block contents at line {}'.format(self.display_name(), self.line))

		single = exec_func.single_command()
		if single == None or self.force_sub_function():
			unique = func.get_unique_id()
			func_name = '{0}{1:03}_ln{2}'.format(self.display_name(), unique, self.line)
			func.register_function(func_name, exec_func)
			
			self.add_continuation_command(func, func_name, exec_func)
			
			func.add_command('{0}run function {1}:{2}'.format(cmd, func.namespace, func_name))			
		else:
			if single.startswith('/'):
				single = single[1:]
				
			if single.startswith('execute '):
				func.add_command(cmd + single[len('execute '):])
			else:
				func.add_command(cmd + 'run ' + single)
				
		self.compile_else(func)
				
	def compile_else(self, func):
		None