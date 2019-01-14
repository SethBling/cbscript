class scratch_tracker(object):
	def __init__(self, global_context):
		self.scratch = {}
		self.temp = {}
		self.global_context = global_context
		self.scratch_allocation = 0
		self.temp_allocation = 0
		self.prefix = ''
		
	def get_temp_var(self):
		for key in self.temp.keys():
			if self.temp[key] == False:
				self.temp[key] = True
				return "temp" + str(key)
		
		newScratch = len(self.temp.keys())
		self.temp[newScratch] = True

		new_length = len(self.temp.keys())
		if new_length > self.temp_allocation:
			self.temp_allocation = new_length
			self.global_context.allocate_temp(new_length)

		return 'temp{1}'.format(self.prefix, newScratch)

	def free_temp_var(self, id):
		num = int(id[len('temp'):])
		
		self.temp[num] = False


	def get_scratch(self):
		for key in self.scratch.keys():
			if self.scratch[key] == False:
				self.scratch[key] = True
				return '{0}_scratch{1}'.format(self.prefix, key)
		
		newScratch = len(self.scratch.keys())
		self.scratch[newScratch] = True
		
		new_length = len(self.scratch.keys())
		if new_length > self.scratch_allocation:
			self.scratch_allocation = new_length
			self.global_context.allocate_scratch(self.prefix, new_length)
		
		return '{0}_scratch{1}'.format(self.prefix, newScratch)
		
	def get_scratch_vector(self):
		return [self.get_scratch() for i in range(3)]

	def is_scratch(self, id):
		scratch_prefix = '{0}_scratch'.format(self.prefix)
		return len(id) >= len(scratch_prefix) and id[:len(scratch_prefix)] == scratch_prefix
		
	def free_scratch(self, id):
		if not self.is_scratch(id):
			return

		scratch_prefix = '{0}_scratch'.format(self.prefix)
		num = int(id[len(scratch_prefix):])
		
		self.scratch[num] = False
		
	def get_allocated_variables(self):
		ret = ['{}_scratch{}'.format(self.prefix, i) for i in range(self.scratch_allocation)]
		ret += ['temp{}'.format(i) for i in range(self.temp_allocation)]
		
		return ret