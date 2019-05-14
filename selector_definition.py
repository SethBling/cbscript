from CompileError import CompileError

def split_qualifier(qualifier):
	for op in ['==', '<=', '>=', '<', '>']:
		if op in qualifier:
			before,after = tuple(qualifier.split(op, 1))
			before = before.strip()
			after = after.strip()
			
			return before, op, after
			
	return None
	
def isNumber(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
		
class selector_definition(object):
	def __init__(self, selector, env):
		self.parts = []
		self.scores_min = {}
		self.scores_max = {}
		self.environment = env
		self.tag = None
		self.paths = {}
		self.vector_paths = {}
		self.pointers = {}
		
		selector = env.apply_replacements(selector)
		
		base_name = selector
		
		if base_name[0] == '@':
			base_name = base_name[1:]
		
		if '[' in base_name:
			base_name = base_name.split('[')[0]
		
		if base_name in env.selectors:
			base_selector = env.selectors[base_name]
			
			self.base_name = base_selector.base_name
			
			for part in base_selector.parts:
				self.parts.append(part)
			
			for var in base_selector.scores_min:
				self.scores_min[var] = base_selector.scores_min[var]
			
			for var in base_selector.scores_max:
				self.scores_max[var] = base_selector.scores_max[var]
				
			for var in base_selector.paths:
				self.paths[var] = base_selector.paths[var]

			for var in base_selector.vector_paths:
				self.vector_paths[var] = base_selector.vector_paths[var]
				
			for var in base_selector.pointers:
				self.pointers[var] = base_selector.pointers[var]
				
			self.tag = base_selector.tag
		else:
			if len(base_name) != 1:
				raise CompileError('Tried to create selector with base name @{0}'.format(base_name))
				
			self.base_name = base_name
				
		if '[' in selector and ']' in selector:
			parts = selector.split('[')[1].split(']')[0].split(',')
			parts = [part.strip() for part in parts]
			
			nbt_part = None
			lbrack = 0
			rbrack = 0
			
			for part in parts:
				if len(part) == 0:
					continue
					
				if part[:3] == 'nbt':
					lbrack = part.count('{')
					rbrack = part.count('}')
					
					if rbrack < lbrack:
						nbt_part = part
						continue
					
				if nbt_part != None:
					lbrack += part.count('{')
					rbrack += part.count('}')
					if rbrack < lbrack:
						nbt_part = nbt_part + ',' + part
						continue
					else:
						part = nbt_part + ',' + part
						nbt_part = None
					
				op_parts = split_qualifier(part)
				if op_parts == None:
					if '=' in part:
						subparts = part.split('=')
						subparts = [part.strip() for part in subparts]
						if subparts[0] == 'type' and subparts[1][:len('minecraft:')] != 'minecraft:' and subparts[1][:len('!minecraft:')] != '!minecraft:':
							if subparts[1][0] == '!':
								subparts[1] = '!minecraft:' + subparts[1][1:]
							else:
								subparts[1] = 'minecraft:' + subparts[1]
						self.parts.append(subparts)
					else:
						if len(part) >= 5 and part[:4].upper() == "NOT ":
							self.scores_max[part[4:]] = 0
							env.register_objective(part[4:])
						else:
							self.scores_min[part] = 1
							env.register_objective(part)
				else:
					before, op, after = op_parts
				
					if not isNumber(after):
						raise SyntaxError('"{0}" is not a number in "{1}"'.format(after, selector))
							
					if op == '==':				
						self.scores_min[before] = int(after)
						self.scores_max[before] = int(after)
					elif op == '<=':
						self.scores_max[before] = int(after)
					elif op == '>=':
						self.scores_min[before] = int(after)
					elif op == '<':
						self.scores_max[before] = int(after)-1
					elif op == '>':
						self.scores_min[before] = int(after)+1
						
					env.register_objective(before)
					
	def compile(self):
		major_parts = []
		
		if len(self.parts) > 0:
			major_parts.append(','.join(['='.join(part) for part in self.parts]))
			
		if len(self.scores_min) != 0 or len(self.scores_max) != 0:
			score_parts = []
				
			for var in self.scores_min:
				if var in self.scores_max:
					if self.scores_min[var] == self.scores_max[var]:
						score_parts.append('{0}={1}'.format(var, self.scores_min[var]))
					else:
						score_parts.append('{0}={1}..{2}'.format(var, self.scores_min[var], self.scores_max[var]))
				else:
					score_parts.append('{0}={1}..'.format(var, self.scores_min[var]))
			for var in self.scores_max:
				if var not in self.scores_min:
					score_parts.append('{0}=..{1}'.format(var, self.scores_max[var]))
			
			major_parts.append('scores={{{0}}}'.format(','.join(score_parts)))
			
		return '@{0}[{1}]'.format(self.base_name, ','.join(major_parts))
		
	def get_type(self):
		for part in self.parts:
			if part[0] == 'type':
				return part[1]
				
		return None
		
	def set_part(self, name, value):
		self.parts = [part for part in self.parts if part[0] != name]
		self.parts.append((name, value))
		
	def single_entity(self):
		if self.base_name == 's' or self.base_name == 'p':
			return True
		
		for part in self.parts:
			if part[0] == 'limit' and part[1] == '1':
				return True
				
		return False