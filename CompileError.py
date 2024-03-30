from traceback import print_exception
from pathlib import Path
from contextvars import ContextVar

cur_file_var = ContextVar("cur_file_var",default=None)

class Pos:
	file: Path
	line: int

	def __init__(self, line: int, file: Path | None = None):
		self.line = line
		self.file = file or cur_file_var.get()

class CompileError(Exception):
	where: None | Pos
	def __init__(self, text, where = None):
		super(Exception, self).__init__(text)
		self.where = where

line_cache = {}

def register_lines(filename: str, lines: list[str]):
	line_cache[filename] = lines

def pretty_print_error(ex: Exception, file = None):
	stack = []
	while (ex.__cause__ is not None):
		stack.append(ex)
		ex = ex.__cause__
	stack.append(ex)
	for e in stack[::-1]:
		if isinstance(e, CompileError):
			print(e,file=file)
			if e.where is not None and e.where.file in line_cache:
				print(f"{e.where.line:>4} |",line_cache[e.where.file][e.where.line-1],file=file)
			continue
		print_exception(e,chain=False, file = file)
