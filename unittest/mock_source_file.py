import time

class mock_source_file(object):
	def __init__(self, base_name='unittest.cbscript', text=''):
		self.base_name = base_name
		self.text = text
		self.time = 0
		
	def get_last_modified(self):
		return time.ctime(self.time)
		
	def get_base_name(self):
		return self.base_name
		
	def get_text(self):
		return self.text