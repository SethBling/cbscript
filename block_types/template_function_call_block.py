from block_base import block_base
from mcfunction import mcfunction
from environment import isNumber, isInt
from variable_types.scoreboard_var import scoreboard_var

class template_function_call_block(block_base):
	def __init__(self, line, function, template_args, args):
		self.line = line
		self.function = function
		self.template_args = template_args
		self.args = args
		
	def compile(self, func):
		function, template_args, args = self.function, self.template_args, self.args
		
		if function not in func.template_functions:
			raise ValueError('Tried to call non-existant template function "{}" at line {}'.format(function, self.line))
		
		template_params, params, sub = func.template_functions[function]
		
		if len(template_args) != len(template_params):
			raise ValueError('Tried to call template function "{}" with {} template arguments ({} expected) at line {}'.format(function, len(template_args), len(template_params), self.line))
			
		if len(args) != len(params):
			raise ValueError('Tried to call template function "{}" with {} function arguments ({} expected) at line {}'.format(function, len(args), len(params), self.line))
		
		# Get textual function name
		func_name = function
		for template_arg in template_args:
			template_arg_val = template_arg.get_value(func)
			func_name = func_name + '_{}'.format(template_arg_val)
		
		if func_name == func.name:
			locals = func.get_all_locals()
			func.push_locals(locals)
		
		# Calculate function arguments
		for i in range(len(args)):
			assignto = 'Param{}'.format(i)
			arg_var = args[i].compile(func, assignto)
			
			param_var = scoreboard_var('Global', assignto)
			param_var.copy_from(func, arg_var)
			
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
				raise Exception('Unable to compile template function contents at line {}'.format(self.line))
			
			# Register the new function
			func.register_function(func_name, new_func)
			
		func.add_command('function {}:{}'.format(func.namespace, func_name))

		if func_name == func.name:
			func.pop_locals(locals)		