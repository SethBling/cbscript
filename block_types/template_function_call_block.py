from .call_block_base import call_block_base
from mcfunction import mcfunction
from environment import isNumber, isInt
from variable_types.scoreboard_var import scoreboard_var

class template_function_call_block(call_block_base):
	def __init__(self, line, function, template_args, args, with_macro_items):
		self.line = line
		self.function = function
		self.template_args = template_args
		self.args = args
		self.with_macro_items = with_macro_items
		
	def compile(self, func):
		function, template_args, args = self.function, self.template_args, self.args
		
		if function not in func.template_functions:
			raise ValueError(f'Tried to call non-existant template function "{function}" at line {self.line}')
		
		template_params, params, sub = func.template_functions[function]
		
		if len(template_args) != len(template_params):
			raise ValueError(f'Tried to call template function "{function}" with {len(template_args)} template arguments ({len(template_params)} expected) at line {self.line}')
			
		if len(args) != len(params):
			raise ValueError(f'Tried to call template function "{function}" with {len(args)} function arguments ({len(params)} expected) at line {self.line}')
		
		# Get textual function name
		func_name = function
		for template_arg in template_args:
			template_arg_val = template_arg.get_value(func)
			# TODO: Replace all invalid function characters with _
			template_arg_val = str(template_arg_val).replace(' ', '_')
			func_name = func_name + f'_{template_arg_val}'
		
		if func_name == func.name:
			locals = func.get_all_locals()
			func.push_locals(locals)

		# Compile macro items if there are any
		self.compile_with_macro_items(func)
		
		# Calculate function arguments
		for i in range(len(args)):
			assignto = scoreboard_var(f'Global', 'Param{i}')
			arg_var = args[i].compile(func, assignto)
			
			assignto.copy_from(func, arg_var)
			
			arg_var.free_scratch(func)
		
		# Compile the function if it doens't exist yet
		if func_name not in func.functions:
			func.functions[func_name] = None
			new_env = func.clone_environment()
			
			# Bind template paramters in the function's environment
			for p in range(len(template_args)):
				new_env.set_dollarid(template_params[p], template_args[p].get_value(func))
			
			# Compile the new function
			new_func = mcfunction(new_env, True, params)
			try:
				new_func.compile_blocks(sub)
			except Exception as e:
				print(e.message)
				raise Exception(f'Unable to compile template function contents at line {self.line}')
			
			# Register the new function
			func.register_function(func_name, new_func)
			
		cmd = f'function {func.namespace}:{func_name}'

		if self.with_macro_items != None:
			cmd = cmd + f'with storage {func.namespace}:global args'
			self.has_macros = True

		func.add_command(cmd)

		if func_name == func.name:
			func.pop_locals(locals)		
