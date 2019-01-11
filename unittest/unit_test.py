import unittest
import mock_source_file
from mock_mcfunction import mock_mcfunction
import mcfunction
import global_context
from block_types.array_assignment_block import array_assignment_block
from block_types.array_definition_block import array_definition_block
from block_types.block_tag_block import block_tag_block
from block_types.command_block import command_block
from block_types.comment_block import comment_block
from block_types.create_block import create_block
from block_types.execute_block import execute_block
from block_types.for_index_block import for_index_block
from block_types.for_selector_block import for_selector_block
from block_types.function_call_block import function_call_block
from block_types.macro_call_block import macro_call_block
from block_types.method_call_block import method_call_block
from block_types.move_block import move_block
from block_types.python_assignment_block import python_assignment_block
from block_types.python_for_block import python_for_block
from block_types.python_if_block import python_if_block
from block_types.scoreboard_assignment_block import scoreboard_assignment_block
from block_types.selector_assignment_block import selector_assignment_block
from block_types.selector_definition_block import selector_definition_block
from block_types.switch_block import switch_block
from block_types.tell_block import tell_block
from block_types.template_function_call_block import template_function_call_block
from block_types.title_block import title_block
from block_types.vector_assignment_block import vector_assignment_block
from block_types.vector_assignment_scalar_block import vector_assignment_scalar_block
from block_types.while_block import while_block
from scalar_expressions.arrayconst_expr import arrayconst_expr
from scalar_expressions.arrayexpr_expr import arrayexpr_expr
from scalar_expressions.binop_expr import binop_expr
from scalar_expressions.create_expr import create_expr
from scalar_expressions.dot_expr import dot_expr
from scalar_expressions.func_expr import func_expr
from scalar_expressions.num_expr import num_expr
from scalar_expressions.scale_expr import scale_expr
from scalar_expressions.selector_expr import selector_expr
from scalar_expressions.selvar_expr import selvar_expr
from scalar_expressions.unary_expr import unary_expr
from vector_expressions.sel_vector_var_expr import sel_vector_var_expr
from vector_expressions.vector_binop_scalar_expr import vector_binop_scalar_expr
from vector_expressions.vector_binop_vector_expr import vector_binop_vector_expr
from vector_expressions.vector_expr import vector_expr
from vector_expressions.vector_here_expr import vector_here_expr
from vector_expressions.vector_var_expr import vector_var_expr

class test_cbscript(unittest.TestCase):
	def test_is_number(self):
		self.assertTrue(mcfunction.isNumber(1))
		self.assertTrue(mcfunction.isNumber(0))
		self.assertTrue(mcfunction.isNumber(1.0))
		self.assertFalse(mcfunction.isNumber(float('inf')))
		self.assertFalse(mcfunction.isNumber(float('nan')))
		self.assertFalse(mcfunction.isNumber(None))
		self.assertFalse(mcfunction.isNumber('test'))
		
	def test_factor(self):
		self.assertEqual(list(mcfunction.factor(20)), [2, 2, 5])
		self.assertEqual(list(mcfunction.factor(2)), [2])
		self.assertEqual(list(mcfunction.factor(1)), [])
		
	def test_compile_runs_without_error(self):
		func = mock_mcfunction()
	
		func.arrays['test'] = (0, 5)
		block = array_assignment_block(0, 'test', 'Const', 1, num_expr(1))
		block.compile(func)
		
		block = array_definition_block(0, 'test', '0', '5')
		block.compile(func)
		
		block = block_tag_block(0, 'test', ['test_block'])
		block.compile(func)
		
		block = command_block(0, 'test')
		block.compile(func)
		
		block = comment_block(0, '#test')
		block.compile(func)
		
		block = create_block(0, '@test', ['0', '0', '0'])
		block.compile(func)
		
		block = execute_block(0, [], [command_block(0, 'test_command')])
		block.compile(func)
		
		block = for_index_block(0, 'test', num_expr(0), num_expr(5), num_expr(2), [command_block(0, 'test_command')])
		block.compile(func)
		
		block = for_selector_block(0, '@test', '@a', [command_block(0, 'test_command')])
		block.compile(func)
		
		block = function_call_block(0, 'test_function', [])
		block.compile(func)
		
		func.macros['test_macro'] = ([], [command_block(0, 'test_command')])
		block = macro_call_block(0, 'test_macro', [])
		block.compile(func)
		
		block = method_call_block(0, '@test_selector', 'test_method', [])
		block.compile(func)
		
		block = move_block(0, '@a', ['0', '0', '0'])
		block.compile(func)
		
		block = python_assignment_block(0, 'test_id', '1+1')
		block.compile(func)
		
		block = python_for_block(0, 'test_id', 'range(3)', [command_block(0, 'test_command')])
		block.compile(func)
		
		block = python_if_block(0, 'True', [command_block(0, 'true_command')], [command_block(0, 'false_command')])
		block.compile(func)
		block = python_if_block(0, 'False', [command_block(0, 'true_command')], [command_block(0, 'false_command')])
		block.compile(func)
		
		var = ('Var', ('@s', 'test'))
		block = scoreboard_assignment_block(0, (var, '+=', num_expr(1)))
		block.compile(func)
		
		block = selector_assignment_block(0, 'test', '@a')
		block.compile(func)
		
		tag = ('Tag', '{}')
		path = ('Path', ('test_path', 'test', 'float', 1000))
		vpath = ('VectorPath', ('test_vector_id', 'test_vector', 'float', 1))
		block = selector_definition_block(0, 'test_id', '@a', [tag, path, vpath])
		block.compile(func)
		
		block = switch_block(0, ('NUM', 1), [])
		block.compile(func)
		case1 = ('python', ('test_id', 'range(3, 6)', [command_block(0, 'test_python')]))
		case2 = ('range', ('1', '2', [command_block(0, 'test_range_1_2')]))
		block = switch_block(0, num_expr(1), [case1, case2])
		block.compile(func)
		
		block = tell_block(0, '@a', '{rhi')
		block.compile(func)
		
		func.template_functions['test_template_function'] = ([], [], [command_block(0, 'test_command')])
		block = template_function_call_block(0, 'test_template_function', [], [])
		block.compile(func)
		
		block = title_block(0, 'subtitle', '@a', ['1', '2', '3'], '{rtest')
		block.compile(func)
		
		var = ('VAR_ID', 'test')
		block = vector_assignment_block(0, var, '+=', vector_here_expr(1000))
		block.compile(func)
		
		var = ('VAR_ID', 'test')
		block = vector_assignment_scalar_block(0, var, '+=', num_expr(1))
		block.compile(func)
		
		block = while_block(0, [], [command_block(0, 'test_command')])
		block.compile(func)
		
	def test_compile_comment(self):
		func = mock_mcfunction()
		block = comment_block(0, '#test')
		block.compile(func)
		self.assertTrue('#test' in func.commands)
			
	def test_compile_command(self):
		func = mock_mcfunction()
		block = command_block(0, 'say hi')
		block.compile(func)
		self.assertTrue('say hi' in func.commands)
		
	def test_compile_move(self):
		func = mock_mcfunction()
		block = move_block(0, '@s', ('1', '1', '1'))
		block.compile(func)
		self.assertTrue('execute at @s run tp @s 1 1 1' in func.commands)

		block = move_block(0, '@a', ('^0', '^0', '^1'))
		block.compile(func)
		self.assertTrue('execute as @a at @s run tp @s ^0 ^0 ^1' in func.commands)
		
	def test_compile_python_assignment(self):
		func = mock_mcfunction()
		
		block = python_assignment_block(0, 'test', '1+1')
		block.compile(func)
		self.assertTrue('test' in func.dollarid)
		self.assertEqual(func.dollarid['test'], 2)
		
		block = python_assignment_block(0, 'test2', '1/0')
		with self.assertRaises(Exception) as context:
			block.compile(func)
		self.assertEqual(len(func.dollarid), 1)

		block = python_assignment_block(0, 'test3', 'math.sqrt(9)')
		block.compile(func)
		self.assertTrue('test3' in func.dollarid)
		self.assertEqual(func.dollarid['test3'], 3)
		
	def test_compile_python_for(self):
		func = mock_mcfunction()
		
		block = python_for_block(0, 'i', 'range(3)', [command_block(0, '/say $i')])
		block.compile(func)
		
		block = python_for_block(0, 'i', '[]', [])
		block.compile(func)
		
		block = python_for_block(0, 'i', '1', [])
		with self.assertRaises(Exception) as context:
			block.compile(func)
	
		block = python_for_block(0, 'i', 'range(1/0)', [])
		with self.assertRaises(Exception) as context:
			block.compile(func)
	
	def test_compile_selector_assignment(self):
		func = mock_mcfunction()
		
		block = selector_assignment_block(0, 'test', '@s[x=1]')
		block.compile(func)
		
		self.assertEqual(func.atid['test'], '@s[x=1]')
		
	def test_compile_array_assignment(self):
		func = mock_mcfunction()
		func.arrays['test_array'] = (0, 5)
		
		block = array_assignment_block(0, 'test_array', 'Const', 1, num_expr(2))
		block.compile(func)
		self.assertTrue('scoreboard players set Global test_array1 2' in func.commands)
		
		func.arrays['test_array2'] = (0, 10)
		block = array_assignment_block(0, 'test_array2', 'Expr', num_expr(2), num_expr(3))
		block.compile(func)
		self.assertTrue('scoreboard players set Global test_array2Val 3' in func.commands)
		self.assertTrue('scoreboard players set Global test_array2Idx 2' in func.commands)
		self.assertTrue('function test_namespace:array_test_array2_set' in func.commands)
		
	def test_compile_array_definition(self):
		func = mock_mcfunction()
		
		block = array_definition_block(0, 'test_array', 0, 5)
		block.compile(func)
		
		self.assertTrue('test_array' in func.arrays)
		self.assertEqual(func.arrays['test_array'], (0, 5))
		
		self.assertEqual(len(func.child_functions), 2)
		self.assertTrue('array_test_array_set' in func.functions)
		self.assertTrue('array_test_array_get' in func.functions)
		
	def test_compile_block_tag(self):
		func = mock_mcfunction()
		
		block = block_tag_block(0, 'test_block_tag', ['test_block'])
		block.compile(func)
		
		self.assertTrue('test_block_tag' in func.block_tags)
		self.assertTrue(func.block_tags['test_block_tag'] == ['test_block'])
		
	def test_compile_create(self):
		func = mock_mcfunction()
		
		block = create_block(0, '@test', ['0', '0', '0'])
		block.compile(func)
		
		self.assertEqual(len(func.created), 1)
		
	def test_compile_execute(self):
		func = mock_mcfunction()
		func.get_execute_command = lambda (x, y): 'execute_command'
		
		block = execute_block(0, [], 'sub')
		block.compile(func)
		
		self.assertEqual(len(func.child_functions), 1)
		
	def test_compile_arrayconst(self):
		func = mock_mcfunction()
		func.arrays['test_array'] = (0, 5)
		
		expr = arrayconst_expr('test_array', '1')
		id = expr.compile(func, None)
		
		self.assertEqual(id, 'test_array1')
		
	def test_compile_arrayexpr_expr(self):
		func = mock_mcfunction()
		func.arrays['test_array'] = (0, 5)
		
		expr = arrayexpr_expr('test_array', num_expr(3))
		id = expr.compile(func, None)
		
		self.assertEqual(id, 'test_arrayVal')
		
	def test_compile_binop_expr(self):
		func = mock_mcfunction()
		
		expr = binop_expr(num_expr(3), '+', num_expr(4))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertTrue('scoreboard players set Global test_id 3' in func.commands)
		self.assertTrue('scoreboard players add Global test_id 4' in func.commands)
		
		expr = binop_expr(num_expr(3), '+', selvar_expr('Global', 'test_var'))
		id = expr.compile(func, 'test_id2')
		
		self.assertEqual(id, 'test_id2')
		self.assertTrue('scoreboard players operation Global test_id2 = Global test_var' in func.commands)
		self.assertTrue('scoreboard players add Global test_id2 3' in func.commands)
		
		expr = binop_expr(num_expr(5), '^', num_expr(2))
		id = expr.compile(func, 'test_id3')
		
		self.assertEqual(id, 'test_scratch')
		self.assertTrue(('Global', 'test_scratch', '=', 'test_id3') in func.operations)
		self.assertTrue(('Global', 'test_scratch', '*=', 'test_id3') in func.operations)
		
		expr = binop_expr(num_expr(5), '^', selvar_expr('Global', 'test_var'))
		id = expr.compile(func, 'test_id4')
		self.assertEqual(id, None)
		
	def test_create_expr(self):
		func = mock_mcfunction()
		
		expr = create_expr(create_block(0, '@test', ['0', '0', '0']))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		
	def test_dot_expr(self):
		func = mock_mcfunction()
		
		expr = dot_expr(vector_var_expr('vec1'), vector_var_expr('vec2'))
		id = expr.compile(func, 'test_id5')
		
		self.assertEqual(id, 'test_scratch')
		self.assertEqual(len(func.commands), 8)
		
	def test_func_expr(self):
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'sin', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		
		expr = func_expr(function_call_block(0, 'cos', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		
		expr = func_expr(function_call_block(0, 'sqrt', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_scratch')
		
		expr = func_expr(function_call_block(0, 'test_function', []))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'ReturnValue')
		self.assertTrue('function test_namespace:test_function' in func.commands)
		
	def test_num_expr(self):
		func = mock_mcfunction()
		
		expr = num_expr(5)
		self.assertEqual(int(expr.const_value(func)), 5)
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertTrue('scoreboard players set Global test_id 5' in func.commands)
		
	def test_scale_expr(self):
		func = mock_mcfunction()
		
		expr = scale_expr()
		self.assertEqual(expr.const_value(func), 1000)
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertTrue('scoreboard players set Global test_id 1000' in func.commands)
	
	def test_selector_expr(self):
		func = mock_mcfunction()
		func.check_single_entity = lambda (x): True
		
		expr = selector_expr('@p')
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
	
	def test_selvar_expr(self):
		func = mock_mcfunction()
		
		expr = selvar_expr('@a', 'test_var')
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertTrue('scoreboard players operation Global test_id = @a test_var' in func.commands)
		
	def test_unary_expr(self):
		func = mock_mcfunction()
		
		expr = unary_expr('-', num_expr(5))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertTrue('scoreboard players set Global test_id 5' in func.commands)
		self.assertTrue('scoreboard players operation Global test_id *= minus Constant' in func.commands)
		
	def test_sel_vector_var_expr(self):
		func = mock_mcfunction()
		
		expr = sel_vector_var_expr('@test', 'test_var')
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		for left, right in [('x', 0), ('y', 1), ('z', 2)]:
			self.assertTrue('scoreboard players operation Global {} = @test _test_var_{}'.format(left, right) in func.commands)
			
	def test_vector_binop_scalar_expr(self):
		func = mock_mcfunction()
		
		expr = vector_binop_scalar_expr(vector_var_expr('test_vector'), '*', num_expr(2))
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		self.assertEqual(func.commands, ['scoreboard players operation Global x = Global _test_vector_0', 'scoreboard players operation Global y = Global _test_vector_1', 'scoreboard players operation Global z = Global _test_vector_2', 'scoreboard players set Global test_scratch 2', 'scoreboard players operation Global x *= Global test_scratch', 'scoreboard players operation Global y *= Global test_scratch', 'scoreboard players operation Global z *= Global test_scratch'])
		
	def test_vector_binop_vector_expr(self):
		func = mock_mcfunction()
		
		expr = vector_binop_vector_expr(vector_var_expr('test_vector1'), '+', vector_var_expr('test_vector2'))
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		self.assertEqual(func.commands, ['scoreboard players operation Global x = Global _test_vector1_0', 'scoreboard players operation Global y = Global _test_vector1_1', 'scoreboard players operation Global z = Global _test_vector1_2', 'scoreboard players operation Global x += Global _test_vector2_0', 'scoreboard players operation Global y += Global _test_vector2_1', 'scoreboard players operation Global z += Global _test_vector2_2'])

	def test_vector_expr(self):
		func = mock_mcfunction()
		
		expr = vector_expr([num_expr(1), num_expr(2), num_expr(3)])
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		for left, right in [('x', 1), ('y', 2), ('z', 3)]:
			self.assertTrue('scoreboard players set Global {} {}'.format(left, right) in func.commands)
			
	def test_vector_here_expr(self):
		func = mock_mcfunction()
		
		expr = vector_here_expr(100)
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		self.assertEqual(func.commands, ['scoreboard players add @e _age 1', 'summon area_effect_cloud', 'scoreboard players add @e _age 1', 'execute store result score Global x run data get entity @e[_age==1,limit=1] Pos[0] 100', 'execute store result score Global y run data get entity @e[_age==1,limit=1] Pos[1] 100', 'execute store result score Global z run data get entity @e[_age==1,limit=1] Pos[2] 100', '/kill @e[_age==1]'])
		
	def test_vector_var_expr(self):
		func = mock_mcfunction()
		
		expr = vector_var_expr('test_vector')
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['_test_vector_0', '_test_vector_1', '_test_vector_2'])
		
if __name__ == '__main__':
    unittest.main()