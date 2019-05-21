from execute_base import execute_base
from CompileError import CompileError

class execute_block(execute_base):
	def __init__(self, line, exec_items, sub, else_sub = None):
		self.line = line
		self.exec_items = exec_items
		self.sub = sub
		self.else_sub = else_sub
		
	def compile(self, func):
		self.perform_execute(func)
		
	def display_name(self):
		return 'execute'
		
	def add_continuation_command(self, func, func_name, exec_func):
		if self.else_sub:
			func.add_command('scoreboard players set Global {} 1'.format(self.scratch))
			exec_func.add_command('scoreboard players set Global {} 0'.format(self.scratch))
			
	def force_sub_function(self):
		return self.else_sub != None
		
	def prepare_scratch(self, func):
		if self.else_sub:
			self.scratch = func.get_scratch()
	
	def compile_else(self, func):
		if self.else_sub == None:
			return
			
		exec_func = func.create_child_function()
		
		try:
			exec_func.compile_blocks(self.else_sub)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile else block contents at line {}'.format(self.display_name(), self.line))
		except Exception as e:
			print(traceback.format_exc())
			raise CompileError('Unable to compile else block contents at line {}'.format(self.display_name(), self.line))
			
		prefix = 'execute if score Global {} matches 1.. '.format(self.scratch)

		single = exec_func.single_command()
		if single == None:
			unique = func.get_unique_id()
			func_name = 'else{0:03}_ln{1}'.format(unique, self.line)
			func.register_function(func_name, exec_func)
			
			func.add_command('{}run function {}:{}'.format(prefix, func.namespace, func_name))
		else:
			if single.startswith('/'):
				single = single[1:]
				
			if single.startswith('execute '):
				func.add_command(prefix + single[len('execute '):])
			else:
				func.add_command(prefix + 'run ' + single)
				
		func.free_scratch(self.scratch)