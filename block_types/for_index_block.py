from .block_base import block_base
import traceback
from CompileError import CompileError, Pos

class for_index_block(block_base):
	def __init__(self, line, var, fr, to, by, sub):
		self.line = line
		self.var = var
		self.fr = fr
		self.to = to
		self.by = by
		self.sub = sub
		
	def compile(self, func):
		var, fr, to, by, sub = self.var, self.fr, self.to, self.by, self.sub
		
		from_var = fr.compile(func, var.get_assignto(func))
		var.copy_from(func, from_var)
		
		to_var = to.compile(func).get_scoreboard_var(func)
			
		if by != None:
			by_var = by.compile(func)
			by_const = by_var.get_const_value(func)
			
			if by_const == None:
				by_var = by_var.get_scoreboard_var(func)
			else:
				by_const = int(by_const)
				
		unique = func.get_unique_id()
		loop_func_name = f'line{self.line:03}/for{unique:03}'

		loop_func = func.create_child_function()
		func.register_function(loop_func_name, loop_func)	

		if var.uses_macro(func): 
			loop_func.has_macros = True

		if to_var.uses_macro(func):
			loop_func.has_macros = True

		if by != None and by_const == None and by_var.uses_macro(func):
			loop_func.has_macros = True
		
		try:
			loop_func.compile_blocks(sub)
		except CompileError as e:
			raise CompileError(f'Unable to compile for block contents at line {self.line}', Pos(self.line)) from e
		except Exception as e:
			raise CompileError(f'Unable to compile for block contents at line {self.line}', Pos(self.line)) from e
		
		if by == None:
			# Use a temporary version of the counting var to work with the scoreboard
			temp_var = var.get_scoreboard_var(func)
			continue_command = f'execute if score {temp_var.get_selvar(func)} <= {to_var.get_selvar(func)} run {loop_func.get_call()}'
			func.add_command(continue_command)
			
			# Add 1 to the counter variable
			loop_func.add_command(f'scoreboard players add {temp_var.get_selvar(func)} 1')
			var.copy_from(func, temp_var)
			
			loop_func.add_command(continue_command)
		else:
			# Use a temporary version of the counting var to work with the scoreboard
			temp_var = var.get_scoreboard_var(func)
			
			if by_const:
				continue_command = f'execute if score {temp_var.get_selvar(func)} {"<=" if by_const >= 0 else ">="} {to_var.get_selvar(func)} run {loop_func.get_call()}'
				func.add_command(continue_command)

				loop_func.add_command(f'scoreboard players {"add" if by_const > 0 else "remove"} {temp_var.get_selvar(func)} {abs(by_const)}')
			else:
				continue_negative_command = f'execute if score {by_var.get_selvar(func)} matches ..-1 if score {temp_var.get_selvar(func)} >= {to_var.get_selvar(func)} run {loop_func.get_call()}'
				continue_positive_command = f'execute if score {by_var.get_selvar(func)} matches 1.. if score {temp_var.get_selvar(func)} <= {to_var.get_selvar(func)} run {loop_func.get_call()}'
				func.add_command(continue_negative_command)
				func.add_command(continue_positive_command)

				loop_func.add_command(f'scoreboard players operation {temp_var.get_selvar(func)} += {by_var.get_selvar(func)}')
				
			var.copy_from(func, temp_var)
			
			if by_const:
				loop_func.add_command(continue_command)
			else:
				loop_func.add_command(continue_negative_command)
				loop_func.add_command(continue_positive_command)				
			
		to_var.free_scratch(func)
		from_var.free_scratch(func)
		if by != None:
			by_var.free_scratch(func)
