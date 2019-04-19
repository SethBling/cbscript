from mcfunction import compile_section

class selector_definition_block(object):
	def __init__(self, line, id, fullselector, items):
		self.line = line
		self.id = id
		self.fullselector = fullselector
		self.items = items
		
	def compile(self, func):
		selector = func.set_atid(self.id, self.fullselector)
		
		for type, val in self.items:
			if type == 'Tag':
				selector.tag = val
			elif type == 'Path':
				path_id, path, data_type, scale = val
				if scale == None:
					scale = func.scale
				else:
					scale = scale.get_value(func)
				selector.paths[path_id] = (path, data_type, scale)
			elif type == 'VectorPath':
				vector_id, path, data_type, scale = val
				if scale == None:
					scale = func.scale
				else:
					scale = scale.get_value(func)
				selector.vector_paths[vector_id] = (path, data_type, scale)
			elif type == 'Method':
				sub_env = func.clone_environment()
				sub_env.update_self_selector('@'+self.id)
				compile_section(val, sub_env)
			elif type == 'Pointer':
				pointer_id, pointer_selector = val
				selector.pointers[pointer_id] = pointer_selector
			else:
				raise ValueError('Unknown selector item type "{0}" in selector definition at line {1}'.format(type, get_line(line)))