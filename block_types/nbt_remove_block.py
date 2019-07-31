from block_base import block_base

class nbt_remove_block(block_base):
	def __init__(self, line, path):
		self.line = line
		self.path = path

	def compile(self, func):
		func.add_command('data remove {}'.format(self.path.get_dest_path(func)))