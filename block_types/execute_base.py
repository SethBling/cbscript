from .block_base import block_base
import traceback
from CompileError import CompileError, Pos

class execute_base(block_base):
	# Override to force the creation of a sub function, even for a single command
	def force_sub_function(self):
		return False
		
	# By default, no continuation is added to the end of the sub function
	def add_continuation_command(self, func, exec_func):
		None
		
	def prepare_scratch(self, func):
		None

	def perform_execute(self, func):
		self.prepare_scratch(func)
		exec_func = func.create_child_function()
		
		cmd = 'execute ' + func.get_execute_items(self.exec_items, exec_func)
		if cmd == None:
			raise CompileError(f'Unable to compile {self.display_name()} block at line {self.line}', Pos(self.line))
		
		try:
			exec_func.compile_blocks(self.sub)
		except CompileError as e:
			raise CompileError(f'Unable to compile {self.display_name()} block contents at line {self.line}', Pos(self.line)) from e
		except Exception as e:
			raise CompileError(f'Unable to compile {self.display_name()} block contents at line {self.line}') from e

		single = exec_func.single_command()
		if single == None or self.force_sub_function():
			unique = func.get_unique_id()
			func_name = f'line{self.line:03}/{self.display_name()}{unique}'
			func.register_function(func_name, exec_func)
			
			self.add_continuation_command(func, exec_func)
			
			func.add_command(f'{cmd}run {exec_func.get_call()}')
		else:
			if single.startswith('/'):
				single = single[1:]

			macro = False
			if single.startswith('$'):
				single = single[1:]
				macro = True

			if single.startswith('execute '):
				cmd = cmd + single[len('execute '):]
			else:
				cmd = cmd + 'run ' + single

			if macro:
				cmd = '$' + cmd

			func.add_command(cmd)
				
		self.compile_else(func)
				
	def compile_else(self, func):
		None
