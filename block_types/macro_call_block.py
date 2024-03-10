from .block_base import block_base
from mcfunction import isNumber
from CompileError import CompileError
import traceback

class macro_call_block(block_base):
	def __init__(self, line, macro, args):
		self.line = line
		self.macro, self.args = macro, args
		
	def compile(self, func):
		if self.macro not in func.macros:
			raise CompileError('Line {1}: macro "{0}" does not exist'.format(self.macro, self.line))
			
		params, sub = func.macros[self.macro]
			
		if len(self.args) != len(params):
			raise CompileError('Tried to call Macro "{0}" with {1} arguments at line {3}, but it requires {2}'.format(macro, len(args), len(params), get_line(line)))
			
		new_env = func.clone_environment()
			
		for p in range(len(params)):
			new_env.set_dollarid(params[p], self.args[p].get_value(func))
				
		func.push_environment(new_env)
		
		try:
			func.compile_blocks(sub)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile macro contents at line {}'.format(self.line))
		except Exception as e:
			print(traceback.format_exc())
			raise CompileError('Unable to compile macro contents at line {}'.format(self.line))
			
		func.pop_environment()