from CompileError import CompileError

class block_switch_base(object):
	def __init__(self):
		self.default_case = None
		for case in self.cases:
			if case.is_default:
				if self.default_case:
					raise CompileError('Block switch at line {} has multiple default cases.'.format(self.line))
				else:
					self.default_case = case
	
		self.block_state_list = {}
		self.block_list = {}
		self.block_state_ids = {}
		self.id_block_states = {}
		
	def compile_initialization(self, func):
		None

	def compile(self, func):
		self.compile_initialization(func)
		blocks = func.get_block_state_list()
		self.get_block_state_list(blocks)
		case_ids = self.get_case_ids()
		self.compile_block_cases(func, case_ids)
		
	def get_quartiles(self, list):
		size = len(list)
		return [
			list[:size/4],
			list[size/4:size/2],
			list[size/2:size*3/4],
			list[size*3/4:]]
	
	def compile_block_cases(self, func, block_cases):
		quartiles = self.get_quartiles(block_cases)
		
		for quartile in quartiles:
			if len(quartile) == 0:
				continue
				
			if len(quartile) == 1:
				block_case = quartile[0]
		
				self.compile_block_case(func, block_case)
			else:
				range_func = func.create_child_function()
				self.compile_block_cases(range_func, quartile)
				
				single_command = range_func.single_command()
				if single_command:
					func.add_command('execute if {} run {}'.format(self.get_range_condition(func, quartile), single_command))
				else:
					unique = func.get_unique_id()
					range_name = 'switch_{}-{}_{}_ln{}'.format(
						str(quartile[0]).replace('minecraft:',''),
						str(quartile[-1]).replace('minecraft:',''),
						unique,
						self.line)
					func.add_command('execute if {} run function {}:{}'.format(
						self.get_range_condition(func, quartile),
						func.namespace,
						range_name))
					func.register_function(range_name, range_func)
			
		
	def get_block_state_name(self, block, state):
		block_state = block + '['
		first = True
		for property in state["properties"]:
			if first:
				first = False
			else:
				block_state += ','
			
			block_state += property
			block_state += '='
			block_state += state["properties"][property]
		
		block_state += ']'
		
		return block_state
		
	def get_block_state_list(self, blocks):
		self.block_state_list = {}
		self.block_list = {}
		
		for block in blocks:
			if "properties" in blocks[block]:
				for state in blocks[block]["states"]:
					block_state = self.get_block_state_name(block, state)
					
					case = self.get_matching_case(block_state)
					if case != None:
						self.block_state_list[block_state] = case
						if block not in self.block_list:
							self.block_list[block] = []
						self.block_list[block].append(block_state)
						self.block_state_ids[block_state] = state["id"]
			else:
				case = self.get_matching_case(block)
				if case != None:
					self.block_state_list[block] = case
					if block not in self.block_list:
						self.block_list[block] = []
					self.block_list[block].append(block)
					self.block_state_ids[block] = blocks[block]["states"][0]["id"]
					
		self.id_block_states = {self.block_state_ids[block_state]:block_state for block_state in self.block_state_ids}
					
	def get_matching_case(self, block_state):
		for case in self.cases:
			if not case.is_default and case.matches(block_state):
				return case
				
		return self.default_case