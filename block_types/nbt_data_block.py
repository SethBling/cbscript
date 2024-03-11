from .block_base import block_base

class nbt_data_block(block_base):
	def __init__(self, line, dest, op, source):
		self.line = line
		self.dest = dest
		self.op = op
		self.source = source

	def compile(self, func):
		func.add_command(f'data modify {self.dest.get_dest_path(func)} {self.op} {self.source.get_source_path(func)}')
