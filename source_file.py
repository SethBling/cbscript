import os
import time
from pathlib import Path

from CompileError import register_lines

class source_file(object):
	filename: Path
	is_log: bool

	def __init__(self, filename, is_log = False):
		if isinstance(filename,str):
			filename = Path(filename)
		self.filename = filename.absolute()
		self.modified = self.get_last_modified()
		if self.filename.exists():
			self.last_size = os.path.getsize(filename)
		self.is_log = is_log
		
	def get_last_modified(self):
		if not self.filename.exists():
			return 0
		return time.ctime(os.path.getmtime(self.filename))
		
	def was_updated(self):
		t = self.get_last_modified()
		if t > self.modified:
			self.modified = t
			return True
		else:
			return False
		
	def get_base_name(self):
		return self.filename.name
		
	def get_directory(self):
		return self.filename.parent
		
	def get_text(self, only_new_text = False):
		text = ""
		while len(text) == 0:
			with open(self.filename, 'r') as content_file:
				if only_new_text:
					content_file.seek(self.last_size)
				text = content_file.read()
				if not self.is_log:
					register_lines(self.filename,text.splitlines())

			# time.sleep(0.1)
			
		self.last_size = os.path.getsize(self.filename)
		return text
