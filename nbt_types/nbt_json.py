class nbt_json(object):
	def __init__(self, json):
		self.json = json
		
	def get_source_path(self, func):
		return 'value {}'.format(self.json)