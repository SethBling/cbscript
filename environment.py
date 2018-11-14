import copy
from scratch_tracker import scratch_tracker
from selector_definition import selector_definition
	
def isNumber(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
		
class environment(object):
	def __init__(self, global_context):
		self.dollarid = {}
		self.global_context = global_context
		self.scratch = scratch_tracker(global_context)
		self.locals = []
		self.selectors = {}
		self.self_selector = None
		
	def clone(self, new_function_name = None):
		new_env = environment(self.global_context)
		
		for id in self.selectors:
			new_env.selectors[id] = self.selectors[id]
		
		new_env.dollarid = copy.deepcopy(self.dollarid)
		if new_function_name == None:
			new_env.scratch = self.scratch
			new_env.locals = self.locals
		else:
			new_env.scratch.prefix = self.global_context.get_scratch_prefix(new_function_name)
			
		new_env.self_selector = self.self_selector
		
		return new_env
		
	def register_local(self, local):
		if local not in self.locals:
			self.locals.append(local)
		
	def apply(self, text):
		text = self.apply_replacements(text)
		text = self.compile_selectors(text)
		
		return text
		
	def apply_replacements(self, text):
		for identifier in reversed(sorted(self.dollarid.keys())):
			text = text.replace('$' + identifier, str(self.dollarid[identifier]))	
				
		return text
	
	def set_dollarid(self, id, val):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0] == '$':
			id = id[1:]
			
		self.dollarid[id] = val
		
	def copy_dollarid(self, id, copyid):
		if len(id) == 0:
			raise Exception('Dollar ID is empty string.')
		
		if id[0].startswith('$'):
			id = id[1:]
		
		if copyid.startswith('$'):
			copyid = copyid[1:]
			
		self.dollarid[id] = self.dollarid[copyid]
		
	def set_atid(self, id, fullselector):
		self.selectors[id] = selector_definition(fullselector, self)
		
		return self.selectors[id]
	
	def compile_selectors(self, command):
		ret = ""
		for fragment in self.split_selectors(command):
			if fragment[0] == "@":
				ret = ret + self.compile_selector(fragment)
			else:
				ret = ret + fragment
				
		return ret		
	
	def get_selector_parts(self, selector):
		if len(selector) == 2:
			selector += "[]"
		
		start = selector[0:3]
		end = selector[-1]
		middle = selector[3:-1]

		parts = middle.split(',')
		
		return start, [part.strip() for part in parts], end
		
	def split_qualifier(self, qualifier):
		for op in ['==', '<=', '>=', '<', '>']:
			if op in qualifier:
				before,after = tuple(qualifier.split(op, 1))
				before = before.strip()
				after = after.strip()
				
				return before, op, after
				
		return None
		
	def compile_selector(self, selector):
		sel = selector_definition(selector, self)
		interpreted = sel.compile()
		
		if len(interpreted) == 4:
			# We have @a[] or similar, so truncate
			interpreted = interpreted[:2]
		
		return interpreted
		
	def get_python_env(self):
		return self.dollarid
		
	def register_objective(self, objective):
		if len(objective) > 16:
			raise Exception('Objective name "{0}" is {1} characters long, max is 16.'.format(objective, len(objective)))
		self.global_context.register_objective(objective)
		
	def split_selectors(self, line):
		fragments = []
		
		remaining = line
		while '@' in remaining:
			parts = remaining.split('@', 1)
			if len(parts[0]) > 0:
				fragments.append(parts[0])

			end = 0
			for i in range(len(parts[1])):
				if parts[1][i].isalnum() or parts[1][i] == '_':
					end += 1
				elif parts[1][i] == '[':
					end = parts[1].find(']')+1
					break
				else:
					break
					
			fragments.append('@' + parts[1][:end])
			remaining = parts[1][end:]
						
		if len(remaining) > 0:
			fragments.append(remaining)
			
		#print(line, fragments)
		
		return fragments
		
	def update_self_selector(self, selector):
		if selector[0] != '@':
			return
			
		id = selector[1:]
		if '[' in id:
			id = id.split('[',1)[0]
			
		if id in self.selectors:
			self.self_selector = self.selectors[id]