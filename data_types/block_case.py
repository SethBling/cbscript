class block_case(object):
	def __init__(self, block_name, block_id, lines, is_default):
		self.block_name = block_name
		self.block_id = block_id
		self.lines = lines
		self.is_default = is_default
		
	def matches(self, block_state):
		if self.block_name.startswith('$'):
			return True
			
		block_name = self.block_name
		if not block_name.startswith('minecraft:'):
			block_name = 'minecraft:' + block_name
			
		return block_state.startswith(block_name)
		
	def compile(self, block_state, block_id, func, falling_block_nbt):
		if self.block_name.startswith('$'):
			func.set_dollarid(self.block_name[1:], block_state)
		if self.block_id.startswith('$'):
			func.set_dollarid(self.block_id[1:], block_id)
			
		func.set_dollarid('falling_block_nbt', falling_block_nbt)
			
		func.compile_blocks(self.lines)