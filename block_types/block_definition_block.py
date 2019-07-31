from block_base import block_base
from data_types.relcoords import relcoords
from CompileError import CompileError

class block_definition_block(block_base):
	def __init__(self, line, block_id, items, coords):
		self.line = line
		self.block_id = block_id
		self.items = items
		self.coords = coords
		self.paths = {}
		
	def compile(self, func):
		func.add_block_definition(self.block_id, self)
		
		for item in self.items:
			self.paths[item.get_name()] = item
		
	def copy_to_objective(self, func, path, coords, macro_args, objective):
		if coords == None:
			coords = self.coords
			
		if path not in self.paths:
			raise CompileError('No path "{}" defined for [{}].'.format(path, self.block_id))
			
		self.paths[id].copy_to_objective(func, coords, macro_args, objective)
		
	def copy_from(self, func, path, coords, macro_args, var):
		if coords == None:
			coords = self.coords
			
		if path not in self.paths:
			raise CompileError('No path "{}" defined for [{}].'.format(path, self.block_id))
			
		self.paths[path].copy_from(func, coords, macro_args, var)
		
	def get_command(self, func, path, coords, macro_args):
		if coords == None:
			coords = self.coords
			
		if path not in self.paths:
			raise CompileError('No path "{}" defined for [{}].'.format(path, self.block_id))
		
		return self.paths[path].get_command(func, coords, macro_args)