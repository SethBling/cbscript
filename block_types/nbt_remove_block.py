class nbt_remove_block(object):
	def __init__(self, line, path):
		self.line = line
		self.path = path

	def compile(self, func):
		func.add_command('data remove {}'.format(self.path.get_dest_path(func)))