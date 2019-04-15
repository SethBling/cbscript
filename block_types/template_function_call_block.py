from mcfunction import mcfunction
from environment import isNumber, isInt

class template_function_call_block(object):
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
			template_arg_val = func.apply_replacements(template_arg)
			func_name = func_name + '_{}'.format(template_arg_val)
		
		# Calculate function arguments
		for i in range(len(args)):
			assignto = 'Param{}'.format(i)
			id = args[i].compile(func, assignto)
			if id == None:
				raise Exception('Unable to compute argument "{}" for template function "{}" at line {}'.format(params[i], function, self.line))

			if id != assignto:
				func.add_command('scoreboard players operation Global {} = Global {}'.format(i, id))
				
			func.free_scratch(id)
		
		# Compile the function if it doens't exist yet
		if func_name not in func.functions:
			new_env = func.clone_environment()
			
			# Bind template paramters in the function's environment
			for p in range(len(template_args)):
				if isInt(template_args[p]):
					new_env.set_dollarid(template_params[p], int(template_args[p]))
				elif isNumber(template_args[p]):
					new_env.set_dollarid(template_params[p], float(template_args[p]))
				elif template_args[p].startswith('"') and template_args.endswith('"') and len(template_args[p]) >= 2:
					new_env.set_dollarid(template_params[p], template_args[p][1:-1])
				elif template_args[p].startswith('$') or template_args[p].startswith('-$'):
					new_env.copy_dollarid(template_params[p], template_args[p])
				else:
					print('Unknown macro parameter "{0}"'.format(template_args[p]))
			
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
	