from mcfunction import get_execute_command

class execute_base(object):
	def perform_execute(self, func, type):
		exec_func = func.create_child_function()
		
		cmd = get_execute_command(self.exec_items, func, exec_func)
		if cmd == None:
			raise Exception('Unable to compile {0} block at line {1}'.format(type.lower(), self.line))
		
		exec_func.compile_blocks(self.sub)

		single = exec_func.single_command()
		if single == None or type == 'While':
			unique = func.get_unique_id()
			func_name = '{0}{1:03}_ln{2}'.format(type.lower(), unique, self.line)
			func.register_function(func_name, exec_func)
			func.add_command('{0}run function {1}:{2}'.format(cmd, func.namespace, func_name))
			
			if type == 'While':
				dummy_func = func.create_child_function()
				sub_cmd = get_execute_command(self.exec_items, exec_func, dummy_func)
				if sub_cmd == None:
					raise Exception('Unable to compile {0} block at line {1}'.format(type.lower(), self.line))

				exec_func.add_command('{0}run function {1}:{2}'.format(cmd, func.namespace, func_name))
		else:
			if single.startswith('/'):
				single = single[1:]
				
			if single.startswith('execute '):
				func.add_command(cmd + single[len('execute '):])
			else:
				func.add_command(cmd + 'run ' + single)