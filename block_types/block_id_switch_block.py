from block_switch_base import block_switch_base
from CompileError import CompileError

class block_id_switch_block(block_switch_base):
	def __init__(self, line, expr, cases):
		self.line = line
		self.expr = expr
		self.cases = cases
		
		super(block_id_switch_block, self).__init__()
		
	def compile_initialization(self, func):
		try:
			var = self.expr.compile(func)
			self.condition_var = var.get_scoreboard_var(func)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile switch expression at line {}.'.format(self.line))
		
	def case_condition(self, block_id):
		return 'score {} {} matches {}'.format(self.condition_var.selector, self.condition_var.objective, block_id)
	
	def compile_block_case(self, func, id):
		case_func = func.create_child_function()
		block_state = self.id_block_states[id]
		
		if block_state not in self.block_state_list:
			return
		
		case = self.block_state_list[block_state]
		falling_block_nbt = self.falling_block_nbt[block_state]
		
		try:
			case.compile(block_state, id, case_func, falling_block_nbt)
		except CompileError as e:
			print(e)
			raise CompileError('Unable to compile block switch at line {}'.format(self.line))
			
		func.call_function(
			case_func,
			'line{:03}/case{}'.format(self.line, id),
			'execute if {} run '.format(self.case_condition(id))
		)
			
	def get_range_condition(self, func, ids):
		return 'score {} {} matches {}..{}'.format(self.condition_var.selector, self.condition_var.objective, ids[0], ids[-1])
		
	def get_case_ids(self):
		return sorted(self.id_block_states.keys())