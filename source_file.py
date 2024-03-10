import os
import time

class source_file(object):
	def __init__(self, filename):
		self.filename = filename
		self.modified = self.get_last_modified()
		self.last_size = os.path.getsize(filename)
		
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
		
	def get_text(self, only_new_text = False):
		text = ""
		while len(text) == 0:
			with open(self.filename, 'rb') as content_file:
				if only_new_text:
					content_file.seek(self.last_size)
				text = content_file.read().decode('utf-8')
			
			time.sleep(0.1)
			
		self.last_size = os.path.getsize(self.filename)
		return text