class for_selector_block(object):
	def __init__(self, line, id, selector, sub):
		self.line = line
		self.id = id
		self.selector = selector
		self.sub = sub
		
	def compile(self, func):
		scratch_id = func.get_scratch()
		
		exec_func = func.create_child_function()
		
		combined_selector = func.get_combined_selector(self.selector)
		combined_selector.scores_min[scratch_id] = 1
		combined_selector.set_part('limit', '1')
		exec_func.selectors[id] = combined_selector
		exec_func.update_self_selector(self.selector)
		
		func.add_command('scoreboard players set {0} {1} 0'.format(self.selector, scratch_id))
		exec_func.add_command('scoreboard players set @s {0} 1'.format(scratch_id))
		
		if not exec_func.compile_blocks(self.sub):
			raise Exception('Unable to compile "for" block at line {}'.format(self.line))
			
		exec_func.add_command('scoreboard players set @s {0} 0'.format(scratch_id))
		
		func.free_scratch(scratch_id)
		
		unique = func.get_unique_id()
		exec_name = 'for{0:03}_ln{1}'.format(unique, self.line)
		func.register_function(exec_name, exec_func)
		
		func.add_command('execute as {0} run function {1}:{2}'.format(self.selector, func.namespace, exec_name))
