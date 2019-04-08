import os
import time

class source_file(object):
	def __init__(self, filename):
		self.filename = filename
		self.modified = self.get_last_modified()
		
	def get_last_modified(self):
		return time.ctime(os.path.getmtime(self.filename))
		
	def was_updated(self):
		t = self.get_last_modified()
		if t > self.modified:
			self.modified = t
			return True
		else:
			return False
		
	def get_base_name(self):
		return os.path.basename(self.filename)
		
	def get_directory(self):
		return os.path.dirname(self.filename)
		
	def get_text(self):
		text = ""
		while len(text) == 0:
			with open(self.filename, 'r') as content_file:
				text = content_file.read()
			
			time.sleep(0.1)
			
		return text