from .block_base import block_base
from mcfunction import isNumber
from CompileError import CompileError, Pos
import traceback

class macro_call_block(block_base):
	def __init__(self, line, macro, args):
		self.line = line
		self.macro, self.args = macro, args
		
	def compile(self, func):
		if self.macro not in func.macros:
			raise CompileError(f'Line {self.line}: macro "{self.macro}" does not exist', Pos(self.line))
			
		params, sub = func.macros[self.macro]
			
		if len(self.args) != len(params):
			raise CompileError(f'Tried to call Macro "{self.macro}" with {len(self.args)} arguments at line {self.line}, but it requires {len(params)}', Pos(self.line))
			
		new_env = func.clone_environment()
			
		for p in range(len(params)):
			new_env.set_dollarid(params[p], self.args[p].get_value(func))
				
		func.push_environment(new_env)
		
		try:
			func.compile_blocks(sub)
		except CompileError as e:
			raise CompileError(f'Unable to compile macro contents at line {self.line}', Pos(self.line)) from e
		except Exception as e:
			raise CompileError(f'Unable to compile macro contents at line {self.line}') from e
			
		func.pop_environment()
