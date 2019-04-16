import new
import unittest

import environment
import global_context
import mcfunction
import scriptparse
import tellraw

from selector_definition import selector_definition
from scratch_tracker import scratch_tracker
from cbscript import cbscript

from mock_block import mock_block
from mock_environment import mock_environment
from mock_global_context import mock_global_context
from mock_mcfunction import mock_mcfunction
from mock_mcworld import mock_mcworld
from mock_parsed import mock_parsed
from mock_selector_definition import mock_selector_definition
from mock_source_file import mock_source_file

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

from data_types.const_number import const_number
from data_types.const_string import const_string
from data_types.python_identifier import python_identifier
from data_types.interpreted_python import interpreted_python
from data_types.relcoord import relcoord
from data_types.relcoords import relcoords

from scalar_expressions.arrayconst_expr import arrayconst_expr
from scalar_expressions.arrayexpr_expr import arrayexpr_expr
from scalar_expressions.binop_expr import binop_expr
from scalar_expressions.create_expr import create_expr
from scalar_expressions.dot_expr import dot_expr
from scalar_expressions.func_expr import func_expr, factor
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

def dummy_relcoords(x, y, z):
	return relcoords((
		relcoord('', const_number(x)),
		relcoord('', const_number(y)),
		relcoord('', const_number(z)),
	))

class test_cbscript(unittest.TestCase):
	def test_is_number(self):
		self.assertTrue(environment.isNumber('1'))
		self.assertTrue(environment.isNumber('0'))
		self.assertTrue(environment.isNumber('1.0'))
		self.assertFalse(environment.isNumber(float('inf')))
		self.assertFalse(environment.isNumber(float('nan')))
		self.assertFalse(environment.isNumber(None))
		self.assertFalse(environment.isNumber('test'))
		
	def test_is_int(self):
		self.assertTrue(environment.isInt('1'))
		self.assertTrue(environment.isInt('0'))
		self.assertFalse(environment.isInt('1.0'))
		self.assertFalse(environment.isInt(float('inf')))
		self.assertFalse(environment.isInt(float('nan')))
		self.assertFalse(environment.isInt(None))
		self.assertFalse(environment.isInt('test'))
		
	def test_factor(self):
		self.assertEqual(list(factor(20)), [2, 2, 5])
		self.assertEqual(list(factor(2)), [2])
		self.assertEqual(list(factor(1)), [])
		
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
		
		block = move_block(0, '@a', dummy_relcoords(0, 0, 0))
		block.compile(func)
		
		block = python_assignment_block(0, 'test_id', interpreted_python('1+1', 0))
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
		path = ('Path', ('test_path', 'test', 'float', const_number(1000)))
		vpath = ('VectorPath', ('test_vector_id', 'test_vector', 'float', const_number(1)))
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
		block = vector_assignment_block(0, var, '+=', vector_here_expr(const_number(1000)))
		block.compile(func)
		
		var = ('VAR_ID', 'test')
		block = vector_assignment_scalar_block(0, var, '+=', num_expr(1))
		block.compile(func)
		
		block = while_block(0, [], [command_block(0, 'test_command')])
		block.compile(func)
		
	def test_compile_vector_assignment_scalar(self):
		func = mock_mcfunction()
		
		block = vector_assignment_scalar_block(0, ('VAR_ID', 'test_vector'), '*=', num_expr(2))
		block.compile(func)
		
		self.assertEqual(len(func.commands), 4)
		self.assertEqual(func.commands[0], 'scoreboard players set Global test_scratch1 2')
		for i in range(3):
			self.assertEqual(func.commands[i+1], 'scoreboard players operation Global _test_vector_{} *= Global test_scratch1'.format(i))
	
	def test_compile_vector_assignment(self):
		func = mock_mcfunction()
		
		block = vector_assignment_block(0, ('VAR_ID', 'test_vector'), '+=', vector_expr([num_expr(2), num_expr(3), num_expr(4)]))
		block.compile(func)
		
		self.assertEqual(len(func.commands), 6)
		for i in range(3):
			self.assertEqual(func.commands[i], 'scoreboard players set Global test_scratch{} {}'.format(i+1, i+2))
			self.assertEqual(func.commands[i+3], 'scoreboard players operation Global _test_vector_{} += Global test_scratch{}'.format(i, i+1))
	
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
		block = move_block(0, '@s', dummy_relcoords(1, 1, 1))
		block.compile(func)
		self.assertTrue('execute at @s run tp @s 1 1 1' in func.commands)

		block = move_block(0, '@a', relcoords((
			relcoord('^', const_number(0)),
			relcoord('^', const_number(0)),
			relcoord('^', const_number(1)),
		)))
		block.compile(func)
		self.assertTrue('execute as @a at @s run tp @s ^0 ^0 ^1' in func.commands)
		
	def test_compile_python_assignment(self):
		func = mock_mcfunction()
		
		block = python_assignment_block(0, 'test', interpreted_python('1+1', 0))
		block.compile(func)
		self.assertTrue('test' in func.dollarid)
		self.assertEqual(func.dollarid['test'], 2)
		
		block = python_assignment_block(0, 'test2', interpreted_python('1/0', 0))
		with self.assertRaises(Exception) as context:
			block.compile(func)
		self.assertEqual(len(func.dollarid), 1)

		block = python_assignment_block(0, 'test3', interpreted_python('math.sqrt(9)', 0))
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
		
		self.assertEqual(func.selectors['test'].selector, '@s[x=1]')
		
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
		
		block = block_tag_block(0, 'test_block_tag', ['test_block', 'test_block2'])
		block.compile(func)
		
		self.assertTrue('test_block_tag' in func.block_tags)
		self.assertTrue(func.block_tags['test_block_tag'] == ['test_block', 'test_block2'])
		
	def test_compile_create(self):
		func = mock_mcfunction()
		
		block = create_block(0, '@test', ['0', '0', '0'])
		block.compile(func)
		
		self.assertEqual(len(func.created), 1)
		
	def test_compile_execute(self):
		func = mock_mcfunction()
		
		block = execute_block(0, 'test', 'sub')
		block.compile(func)
		
		self.assertEqual(len(func.child_functions), 1)
		self.assertEqual(func.execute_command_calls, ['test'])
		
	def test_compile_for_selector(self):
		func = mock_mcfunction()
		
		block = for_selector_block(0, 'test', '@a', command_block(1, 'test_command'))
		block.compile(func)
		
		self.assertEqual(len(func.child_functions), 1)
		self.assertTrue('test' in func.child_functions[0].selectors)
		
	def test_compile_for_index(self):
		func = mock_mcfunction()
		
		block = for_index_block(0, 'test_idx', num_expr(1), num_expr(5), num_expr(2), [])
		block.compile(func)
		
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_idx 1',
			'scoreboard players set Global test_scratch1 5',
			'scoreboard players set Global test_scratch2 2',
			'execute if score Global test_scratch2 matches ..-1 if score Global test_idx >= Global test_scratch1 run function test_namespace:for001_ln0',
			'execute if score Global test_scratch2 matches 1.. if score Global test_idx <= Global test_scratch1 run function test_namespace:for001_ln0'
		])
		
		self.assertEqual(len(func.child_functions), 1)
		self.assertEqual(func.child_functions[0].commands, [
			'scoreboard players operation Global test_idx += Global test_scratch2',
			'execute if score Global test_scratch2 matches ..-1 if score Global test_idx >= Global test_scratch1 run function test_namespace:for001_ln0',
			'execute if score Global test_scratch2 matches 1.. if score Global test_idx <= Global test_scratch1 run function test_namespace:for001_ln0'
		])
		
	def test_compile_function_call(self):
		func = mock_mcfunction()
		
		block = function_call_block(0, 'test_function', [num_expr(1)])
		block.compile(func)

		self.assertEqual(func.commands, ['function test_namespace:test_function'])
		
	def test_compile_macro_call(self):
		func = mock_mcfunction()
		macro = (['test_param'],[])
		func.macros['test_macro'] = macro
		
		block = macro_call_block(0, 'test_macro', [const_number('10')])
		block.compile(func)
		
		self.assertEqual(len(func.child_functions), 0)
		self.assertEqual(len(func.cloned_environments), 1)
		self.assertTrue('test_param' in func.cloned_environments[0].dollarid)
		self.assertEqual(func.cloned_environments[0].dollarid['test_param'], 10)
		
		self.assertEqual(func.environment_pushes, 1)
		self.assertEqual(func.environment_pops, 1)
		
	def test_compile_method_call(self):
		func = mock_mcfunction()
		
		block = method_call_block(0, '@test_selector', 'test_method', [num_expr(1)])
		block.compile(func)
		
		self.assertEqual(func.commands, ['execute as @test_selector run function test_namespace:test_method'])
		
	def test_compile_python_if(self):
		func = mock_mcfunction()
		
		block = python_if_block(0, 'True', [1], [2])
		block.compile(func)
		
		self.assertTrue([1] in func.compiled_blocks)
		
		func = mock_mcfunction()
		
		block = python_if_block(0, 'False', [1], [2])
		block.compile(func)
		
		self.assertTrue([2] in func.compiled_blocks)
		
		func = mock_mcfunction()
		
		block = python_if_block(0, 'True', [1], None)
		block.compile(func)
		
		self.assertTrue([1] in func.compiled_blocks)
		
		func = mock_mcfunction()
		
		block = python_if_block(0, 'False', [1], None)
		block.compile(func)
		
		self.assertEqual(len(func.compiled_blocks), 0)
		
	def test_compile_scoreboard_assignment(self):
		func = mock_mcfunction()
		
		var = ('Var', ('Global', 'test_var'))
		block = scoreboard_assignment_block(0, (var, '+=', num_expr(1)))
		block.compile(func)
		
		self.assertEqual(func.commands, ['/scoreboard players add Global var1 1'])
		
		func = mock_mcfunction()
		
		block = scoreboard_assignment_block(0, (var, '=', num_expr(1)))
		block.compile(func)
		
		self.assertEqual(func.commands, ['/scoreboard players set Global var1 1'])
		
		func = mock_mcfunction()
		
		block = scoreboard_assignment_block(0, (var, '*=', num_expr(1)))
		block.compile(func)
		
		self.assertEqual(func.commands, ['/scoreboard players operation Global var1 *= test_constant Constant'])
		self.assertTrue(1 in func.constants)
		
	def test_compile_selector_definition(self):
		func = mock_mcfunction()
		
		items = [
			('Tag', '{}'),
			('Path', ('test_path', 'path.to.data', 'float', const_number(100))),
			('VectorPath', ('test_vector_path', 'path.to.vector', 'int', const_number(200))),
			('Method', ('function', 'test_method', [], [], [])),
		]
		block = selector_definition_block(0, 'test_selector', '@a', items)
		block.compile(func)
		
		self.assertTrue('test_selector' in func.selectors)

		selector = func.selectors['test_selector']
		self.assertEqual(selector.selector, '@a')

		self.assertTrue('test_path' in selector.paths)
		self.assertEqual(selector.paths['test_path'], ('path.to.data', 'float', 100))

		self.assertTrue('test_vector_path' in selector.vector_paths)
		self.assertEqual(selector.vector_paths['test_vector_path'], ('path.to.vector', 'int', 200))
		
		# TODO: verify the method was created
		
	def test_compile_switch(self):
		func = mock_mcfunction()
		
		case1 = ('range',(1, 3, []))
		case2 = ('python', ('test_id', 'range(4, 6)', []))
		block = switch_block(0, num_expr(2), [case1, case2])
		block.compile(func)
		
		self.assertEqual(func.switch_calls, [(
			'test_scratch1',
			[
				(1, 3, [], 'Unknown', None),
				(4, 4, [], 'Unknown', 'test_id'),
				(5, 5, [], 'Unknown', 'test_id')
			],
			'switch',
			'case')
		])
		self.assertEqual(func.commands, ['scoreboard players set Global test_scratch1 2'])
		
	def test_compile_tell(self):
		func = mock_mcfunction()
		
		block = tell_block(0, '@a', '{rhi')
		block.compile(func)
		
		self.assertEqual(func.commands, ['/tellraw @a ["",{"text":"hi","color":"dark_red"}]'])
		
	def test_compile_template_function_call(self):
		func = mock_mcfunction()
		func.template_functions['test_template_function'] = (['test_macro_param'], ['test_function_param'], [])
		
		block = template_function_call_block(0, 'test_template_function', [const_number('10')], [num_expr('15')])
		block.compile(func)
		
		self.assertEqual(func.commands, [
			'scoreboard players set Global Param0 15',
			'function test_namespace:test_template_function_10'
		])
		self.assertTrue('test_template_function_10' in func.functions)
		self.assertTrue('test_macro_param' in func.functions['test_template_function_10'].environment.dollarid)
		self.assertEqual(func.functions['test_template_function_10'].environment.dollarid['test_macro_param'], 10)
		
		func = mock_mcfunction()
		func.template_functions['test_template_function'] = (['test_macro_param'], [], [])
		func.dollarid['test_id'] = 5
		
		block = template_function_call_block(0, 'test_template_function', [python_identifier('test_id')], [])
		block.compile(func)
		
		self.assertTrue('test_template_function_5' in func.functions)
		self.assertEqual(func.functions['test_template_function_5'].environment.dollarid['test_macro_param'], 5)
		
	def test_compile_title(self):
		func = mock_mcfunction()
		
		block = title_block(0, 'subtitle', '@a', ['0', '1', '2'], '{rtest')
		block.compile(func)
		
		self.assertEqual(func.commands, [
			'/title @a times 0 1 2',
			'/title @a subtitle ["",{"text":"test","color":"dark_red"}]'
		])
		
	def test_compile_while(self):
		func = mock_mcfunction()
		
		block = while_block(0, 'test', ['test_block'])
		block.compile(func)
		
		self.assertEqual(func.commands, ['execute_dummy run function test_namespace:while001_ln0'])
		self.assertEqual(func.execute_command_calls, ['test'])
		self.assertEqual(len(func.child_functions), 1)
		self.assertEqual(func.child_functions[0].compiled_blocks[0], ['test_block'])
		self.assertTrue('execute_dummy run function test_namespace:while001_ln0' in func.child_functions[0].commands)
		
	def test_arrayconst_expr(self):
		func = mock_mcfunction()
		func.arrays['test_array'] = (0, 5)
		
		expr = arrayconst_expr('test_array', '1')
		id = expr.compile(func, None)
		
		self.assertEqual(id, 'test_array1')
		
	def test_arrayexpr_expr(self):
		func = mock_mcfunction()
		func.arrays['test_array'] = (0, 5)
		
		expr = arrayexpr_expr('test_array', num_expr(3))
		id = expr.compile(func, None)
		
		self.assertEqual(id, 'test_arrayVal')
		
	def test_binop_expr(self):
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
		
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_id 3',
			'scoreboard players add Global test_id 4',
			'scoreboard players operation Global test_id2 = Global test_var',
			'scoreboard players add Global test_id2 3',
			'scoreboard players set Global test_id3 5',
			'scoreboard players operation Global test_scratch1 = Global test_id3',
			'scoreboard players operation Global test_scratch1 *= Global test_id3'
		])
		
		expr = binop_expr(num_expr(5), '^', selvar_expr('Global', 'test_var'))
		id = expr.compile(func, 'test_id4')
		self.assertEqual(id, None)
		
	def test_create_expr(self):
		func = mock_mcfunction()
		
		expr = create_expr(create_block(0, '@test', ['0', '0', '0']))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertEqual(func.commands, [
			'scoreboard players add @e _age 1',
			'scoreboard players add @e _age 1',
			'scoreboard players add Global _unique 1',
			'scoreboard players operation @@test[_age==1] _id = Global _unique',
			'scoreboard players operation Global test_id = Global _unique'])
		self.assertEqual(func.created, [('@test', ['0', '0', '0'])])
		
	def test_dot_expr(self):
		func = mock_mcfunction()
		
		expr = dot_expr(vector_var_expr('vec1'), vector_var_expr('vec2'))
		id = expr.compile(func, 'test_id5')
		
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(len(func.commands), 8)
		
	def test_func_expr(self):
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'sin', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_scratch1 1',
			'scoreboard players operation Global temp1 = Global test_scratch1',
			'scoreboard players operation Global temp1 %= test_constant Constant',
			'scoreboard players add Global temp1 360',
			'scoreboard players operation Global temp1 %= test_constant Constant',
			'scoreboard players operation Global test_id = Global test_scratch1',
			'scoreboard players operation Global temp2 = Global temp1',
			'scoreboard players operation Global temp2 %= test_constant Constant',
			'scoreboard players operation Global test_id = Global temp2',
			'scoreboard players operation Global test_id *= test_constant Constant',
			'scoreboard players set Global test_scratch2 180',
			'scoreboard players operation Global test_scratch3 = Global test_scratch2',
			'scoreboard players operation Global test_scratch3 -= Global temp2',
			'scoreboard players operation Global test_id *= Global test_scratch3',
			'scoreboard players set Global test_scratch4 40500',
			'scoreboard players operation Global test_scratch5 = Global test_scratch4',
			'scoreboard players operation Global test_scratch6 = Global temp2',
			'scoreboard players set Global test_scratch7 180',
			'scoreboard players operation Global test_scratch8 = Global test_scratch7',
			'scoreboard players operation Global test_scratch8 -= Global temp2',
			'scoreboard players operation Global test_scratch6 *= Global test_scratch8',
			'scoreboard players operation Global test_scratch5 -= Global test_scratch6',
			'scoreboard players operation Global test_id /= Global test_scratch5',
			'execute if score Global temp1 matches 180.. run scoreboard players operation Global test_id *= minus Constant'
		])
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'cos', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_scratch1 1',
			'scoreboard players operation Global temp1 = Global test_scratch1', 
			'scoreboard players operation Global temp1 %= test_constant Constant', 
			'scoreboard players add Global temp1 450', 
			'scoreboard players operation Global temp1 %= test_constant Constant', 
			'scoreboard players operation Global test_id = Global test_scratch1', 
			'scoreboard players operation Global temp2 = Global temp1', 
			'scoreboard players operation Global temp2 %= test_constant Constant', 
			'scoreboard players operation Global test_id = Global temp2', 
			'scoreboard players operation Global test_id *= test_constant Constant', 
			'scoreboard players set Global test_scratch2 180', 
			'scoreboard players operation Global test_scratch3 = Global test_scratch2', 
			'scoreboard players operation Global test_scratch3 -= Global temp2', 
			'scoreboard players operation Global test_id *= Global test_scratch3', 
			'scoreboard players set Global test_scratch4 40500', 
			'scoreboard players operation Global test_scratch5 = Global test_scratch4', 
			'scoreboard players operation Global test_scratch6 = Global temp2', 
			'scoreboard players set Global test_scratch7 180', 
			'scoreboard players operation Global test_scratch8 = Global test_scratch7', 
			'scoreboard players operation Global test_scratch8 -= Global temp2', 
			'scoreboard players operation Global test_scratch6 *= Global test_scratch8', 
			'scoreboard players operation Global test_scratch5 -= Global test_scratch6', 
			'scoreboard players operation Global test_id /= Global test_scratch5', 
			'execute if score Global temp1 matches 180.. run scoreboard players operation Global test_id *= minus Constant'
		])
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'sqrt', [num_expr(1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_scratch62')
		self.assertEqual(len(func.commands), 107)
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'sqrt', []))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, None)
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'abs', [num_expr(-1)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_id')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_id -1',
			'execute if score Global test_id matches ..-1 run scoreboard players operation Global test_id *= minus Constant'
		])
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'abs', []))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, None)
		
		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'rand', [num_expr(10)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_scratch1 0',
			'scoreboard players operation Global test_scratch1 += @e[type=armor_stand, test_random_objective <= 1, limit=1, sort=random] test_random_objective',
			'scoreboard players operation Global test_scratch1 *= test_constant Constant',
			'scoreboard players operation Global test_scratch1 += @e[type=armor_stand, test_random_objective <= 4, limit=1, sort=random] test_random_objective'
		])

		func = mock_mcfunction()
		
		expr = func_expr(function_call_block(0, 'rand', [num_expr(2), num_expr(10)]))
		id = expr.compile(func, 'test_id')
		
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_scratch1 0',
			'scoreboard players operation Global test_scratch1 += @e[type=armor_stand, test_random_objective <= 1, limit=1, sort=random] test_random_objective',
			'scoreboard players operation Global test_scratch1 *= test_constant Constant', 'scoreboard players operation Global test_scratch1 += @e[type=armor_stand, test_random_objective <= 1, limit=1, sort=random] test_random_objective',
			'scoreboard players operation Global test_scratch1 *= test_constant Constant', 'scoreboard players operation Global test_scratch1 += @e[type=armor_stand, test_random_objective <= 1, limit=1, sort=random] test_random_objective',
			'scoreboard players add Global test_scratch1 2'
		])
		
		func = mock_mcfunction()
		
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
		self.assertEqual(func.commands, [
			'scoreboard players add Global _unique 1',
			'execute unless score @p _id matches 0.. run scoreboard players operation @p _id = Global _unique',
			'scoreboard players operation Global test_id = @p _id'
		])
	
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
		self.assertEqual(func.commands, [
			'scoreboard players operation Global x = Global _test_vector_0',
			'scoreboard players operation Global y = Global _test_vector_1',
			'scoreboard players operation Global z = Global _test_vector_2',
			'scoreboard players set Global test_scratch1 2',
			'scoreboard players operation Global x *= Global test_scratch1',
			'scoreboard players operation Global y *= Global test_scratch1',
			'scoreboard players operation Global z *= Global test_scratch1'
		])
		
	def test_vector_binop_vector_expr(self):
		func = mock_mcfunction()
		
		expr = vector_binop_vector_expr(vector_var_expr('test_vector1'), '+', vector_var_expr('test_vector2'))
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		self.assertEqual(func.commands, [
			'scoreboard players operation Global x = Global _test_vector1_0',
			'scoreboard players operation Global y = Global _test_vector1_1',
			'scoreboard players operation Global z = Global _test_vector1_2',
			'scoreboard players operation Global x += Global _test_vector2_0',
			'scoreboard players operation Global y += Global _test_vector2_1',
			'scoreboard players operation Global z += Global _test_vector2_2'
		])

	def test_vector_expr(self):
		func = mock_mcfunction()
		
		expr = vector_expr([num_expr(1), num_expr(2), num_expr(3)])
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		for left, right in [('x', 1), ('y', 2), ('z', 3)]:
			self.assertTrue('scoreboard players set Global {} {}'.format(left, right) in func.commands)
			
	def test_vector_here_expr(self):
		func = mock_mcfunction()
		
		expr = vector_here_expr(const_number(100))
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['x', 'y', 'z'])
		self.assertEqual(func.commands, [
			'scoreboard players add @e _age 1',
			'summon area_effect_cloud',
			'scoreboard players add @e _age 1',
			'execute store result score Global x run data get entity @e[_age==1,limit=1] Pos[0] 100',
			'execute store result score Global y run data get entity @e[_age==1,limit=1] Pos[1] 100',
			'execute store result score Global z run data get entity @e[_age==1,limit=1] Pos[2] 100',
			'/kill @e[_age==1]'
		])
		
	def test_vector_var_expr(self):
		func = mock_mcfunction()
		
		expr = vector_var_expr('test_vector')
		ids = expr.compile(func, ['x', 'y', 'z'])
		
		self.assertEqual(ids, ['_test_vector_0', '_test_vector_1', '_test_vector_2'])
		
	def test_selector_definition(self):
		env = mock_environment()
		
		sel = selector_definition('@a', env)
		self.assertEqual(sel.compile(), '@a[]')
		
		env = mock_environment()
		
		sel = selector_definition('@a[test>0]', env)
		self.assertEqual(sel.compile(), '@a[scores={test=1..}]')
		
		env = mock_environment()
		env.selectors['test_selector'] = selector_definition('@a[nbt={test:"test_val"}]', env)
		
		sel = selector_definition('@test_selector[nbt={test2:"test_val2"}]', env)
		# TODO: merge nbt tags via the json module
		self.assertEqual(sel.compile(), '@a[nbt={test:"test_val"},nbt={test2:"test_val2"}]')
		
		env = mock_environment()
		
		sel = selector_definition('@a[test==0]', env)
		self.assertEqual(sel.compile(), '@a[scores={test=0}]')
		
		env = mock_environment()
		
		sel = selector_definition('@a[test>=0,test<=0]', env)
		self.assertEqual(sel.compile(), '@a[scores={test=0}]')
		
		env = mock_environment()
		
		sel = selector_definition('@e[type=creeper]', env)
		self.assertEqual(sel.compile(), '@e[type=minecraft:creeper]')
		self.assertEqual(sel.get_type(), 'minecraft:creeper')
		self.assertFalse(sel.single_entity())
		
		env = mock_environment()
		
		sel = selector_definition('@e[limit=1]', env)
		self.assertTrue(sel.single_entity())
		
		env = mock_environment()
		
		sel = selector_definition('@p', env)
		self.assertTrue(sel.single_entity())
		
		env = mock_environment()
		
		sel = selector_definition('@s', env)
		self.assertTrue(sel.single_entity())		
		
		env = mock_environment()
		env.selectors['test_selector'] = selector_definition('@e[test==0]', env)
		env.selectors['test_selector'].set_part('type', 'creeper')
		env.selectors['test_selector'].paths['test_path'] = 1
		env.selectors['test_selector'].vector_paths['test_vector_path'] = 2
		
		sel = selector_definition('@test_selector[test2>0]', env)
		self.assertEqual(sel.compile(), '@e[type=creeper,scores={test=0,test2=1..}]')
		self.assertEqual(sel.paths['test_path'], 1)
		self.assertEqual(sel.vector_paths['test_vector_path'], 2)
		
		env = mock_environment()
		
		with self.assertRaises(ValueError):
			selector_definition('@none', env)
			
		env = mock_environment()
		
		sel = selector_definition('@e[nbt={test:"test_val",test2:{test3:"test_val3"}}]', env)
		# TODO: merge nbt tags via the json module
		self.assertEqual(sel.compile(), '@e[nbt={test:"test_val",test2:{test3:"test_val3"}}]')
		
		env = mock_environment()
		
		with self.assertRaises(SyntaxError):
			sel = selector_definition('@a[test>test2]', env)
			
	def test_get_friendly_name(self):
		self.assertEqual(global_context.get_friendly_name('test .,:{}='), 'CBtest_______')
		
	def test_global_context_register_block_tag(self):
		gc = global_context.global_context('test_namespace')
		
		gc.register_block_tag('test_block_tag', ['test_block'])
		self.assertEqual(gc.block_tags['test_block_tag'], ['test_block'])
	
	def test_global_context_get_unique_id(self):
		gc = global_context.global_context('test_namespace')
		
		self.assertEqual(gc.get_unique_id(), 1)
		self.assertEqual(gc.get_unique_id(), 2)
		
	def test_global_context_register_clock(self):
		gc = global_context.global_context('test_namespace')
		
		gc.register_clock('test_clock')
		self.assertEqual(gc.clocks, ['test_clock'])
	
	def test_global_context_register_function(self):
		gc = global_context.global_context('test_namespace')
		f = mock_mcfunction()
		
		gc.register_function('test_function', f)
		self.assertEqual(gc.functions['test_function'], f)
		with self.assertRaises(Exception):
			gc.register_function('test_function', f)
	
	def test_global_context_register_array(self):
		gc = global_context.global_context('test_namespace')
		
		gc.register_array('test_array', 0, 5)
		self.assertEqual(gc.arrays['test_array'], (0, 5))
		with self.assertRaises(Exception):
			gc.register_array('test_array', 0, 5)
	
	def test_global_context_register_objective(self):
		gc = global_context.global_context('test_namespace')
		
		gc.register_objective('test_objective')
		self.assertTrue('test_objective' in gc.objectives)
		
		with self.assertRaises(Exception):
			gc.register_objective('test_objective_name_too_long')
			
	def test_global_context_get_constant_name(self):
		gc = global_context.global_context('test_namespace')
		f = mock_mcfunction()
	
		gc.register_function('reset', f)
		self.assertEqual(gc.get_reset_function(), f)

		self.assertEqual(global_context.get_constant_name(0), 'c0')
		self.assertEqual(global_context.get_constant_name(1), 'c1')
		self.assertEqual(global_context.get_constant_name(-1), 'minus')
		self.assertEqual(global_context.get_constant_name(-2), 'cm2')
	
	def test_global_context_add_constant(self):
		gc = global_context.global_context('test_namespace')
		
		self.assertEqual(gc.add_constant(1), 'c1')
		self.assertTrue(1 in gc.constants)
	
	def test_global_context_add_constant_definitions(self):
		gc = global_context.global_context('test_namespace')
		f = mock_mcfunction()
		
		gc.register_function('reset', f)
		gc.add_constant(1)
		gc.add_constant(-1)
		gc.add_constant_definitions()
		
		self.assertEqual(f.commands, [
			'/scoreboard objectives add Constant dummy',
			'/scoreboard players set minus Constant -1',
			'/scoreboard players set c1 Constant 1'
		])
	
	def test_global_context_allocate_scratch(self):
		gc = global_context.global_context('test_namespace')
		
		gc.allocate_scratch('test_prefix', 2)
		self.assertEqual(gc.scratch['test_prefix'], 2)
		gc.allocate_scratch('test_prefix', 3)
		self.assertEqual(gc.scratch['test_prefix'], 3)
		gc.allocate_scratch('test_prefix', 2)
		self.assertEqual(gc.scratch['test_prefix'], 3)
	
	def test_global_context_allocate_temp(self):
		gc = global_context.global_context('test_namespace')
		
		gc.allocate_temp(2)
		self.assertEqual(gc.temp, 2)
		gc.allocate_temp(3)
		self.assertEqual(gc.temp, 3)
		gc.allocate_temp(2)
		self.assertEqual(gc.temp, 3)
	
	def test_global_context_allocate_rand(self):
		gc = global_context.global_context('test_namespace')
		
		gc.allocate_rand(2)
		self.assertEqual(gc.rand, 2)
		gc.allocate_rand(3)
		self.assertEqual(gc.rand, 3)
		gc.allocate_rand(2)
		self.assertEqual(gc.rand, 3)
		
	def test_global_context_finalize_functions(self):
		gc = global_context.global_context('test_namespace')
		f = mock_mcfunction()
		
		gc.register_function('reset', f)
		gc.finalize_functions()
		
		self.assertTrue(f.finalized)
		
	def test_global_context_get_scratch_prefix(self):
		gc = global_context.global_context('test_namespace')
		
		self.assertEqual(gc.get_scratch_prefix('test'), 'tes')
		self.assertEqual(gc.get_scratch_prefix('test'), 'tes2')
		self.assertEqual(gc.get_scratch_prefix('test'), 'tes3')
	
	def test_global_context_get_random_objective(self):
		gc = global_context.global_context('test_namespace')
		
		self.assertEqual(gc.get_random_objective(), 'RVtest_namespace')
		
	def test_scratch_tracker_temp(self):
		gc = mock_global_context()
		
		st = scratch_tracker(gc)
		self.assertEqual(st.get_temp_var(), 'temp0')
		self.assertEqual(st.temp[0], True)
		self.assertEqual(st.get_temp_var(), 'temp1')
		self.assertEqual(st.temp[1], True)
		st.free_temp_var('temp0')
		self.assertEqual(st.temp[0], False)
		self.assertEqual(st.temp[1], True)
		self.assertEqual(gc.temp, 2)
		self.assertEqual(st.get_temp_var(), 'temp0')
		
	def test_scratch_tracker_scratch(self):
		gc = mock_global_context()
		
		st = scratch_tracker(gc)
		st.prefix = 'test'
		self.assertEqual(st.get_scratch(), 'test_scratch0')
		self.assertEqual(st.scratch[0], True)
		self.assertEqual(st.get_scratch(), 'test_scratch1')
		self.assertEqual(st.scratch[1], True)
		st.free_scratch('test_scratch0')
		self.assertEqual(st.scratch[0], False)
		self.assertEqual(st.scratch[1], True)
		self.assertEqual(gc.scratch['test'], 2)
		self.assertEqual(st.get_scratch(), 'test_scratch0')
		
		st.free_scratch('not_scratch')

	def test_scratch_tracker_vector(self):
		gc = mock_global_context()
		
		st = scratch_tracker(gc)
		st.prefix = 'test'
		
		self.assertEqual(st.get_scratch_vector(), ['test_scratch0', 'test_scratch1', 'test_scratch2'])
		self.assertEqual(gc.scratch['test'], 3)
		for i in range(3):
			self.assertEqual(st.scratch[i], True)
		
	def test_scratch_tracker_get_allocated_variables(self):
		gc = mock_global_context()
		
		st = scratch_tracker(gc)
		st.prefix = 'test'
		
		st.get_scratch()
		st.get_scratch()
		st.get_scratch()
		st.free_scratch('test_scratch1')
		
		st.get_temp_var()
		st.get_temp_var()
		st.get_temp_var()
		st.free_temp_var('temp0')
		
		self.assertEqual(st.get_allocated_variables(), [
			'test_scratch0',
			'test_scratch1',
			'test_scratch2',
			'temp0',
			'temp1',
			'temp2'
		])
		
	def test_cbscript_check_for_update(self):
		source = mock_source_file()
		source.updated = False
		
		compiles = [0]
		
		script = cbscript(source, None)
		script.compiles = 0
		
		def count_compiles(self):
			self.compiles += 1
		script.try_to_compile = new.instancemethod(count_compiles, script, None)
		
		self.assertEqual(script.compiles, 0)
		script.check_for_update()
		self.assertEqual(script.compiles, 0)
		source.updated = True
		script.check_for_update()
		self.assertEqual(script.compiles, 1)
		
	def test_cbscript_try_to_compile(self):
		source = mock_source_file()
		
		script = cbscript(source, None)
		script.log_lines = []
		def mock_log(self, text):
			self.log_lines.append(text)
		script.log = new.instancemethod(mock_log, script, None)
		script.compile_all = new.instancemethod(lambda s: True, script, None)
		
		script.try_to_compile()
		self.assertEqual(script.log_lines, [
			'Compiling unittest...',
			'Script successfully applied.'
		])
		
		script = cbscript(source, None)
		script.log_lines = []
		script.log = new.instancemethod(mock_log, script, None)
		script.compile_all = new.instancemethod(lambda s: False, script, None)
		
		script.try_to_compile()
		self.assertEqual(script.log_lines, [
			'Compiling unittest...',
			'Script had compile error(s).\x07'
		])
		
		def bad_parse(text):
			raise SyntaxError('Test error')
		script = cbscript(source, bad_parse)
		script.log_lines = []
		script.log = new.instancemethod(mock_log, script, None)
		
		script.try_to_compile()
		self.assertEqual(script.log_lines, [
			'Compiling unittest...',
			'Test error\x07'
		])
		
		def bad_compile(text):
			raise Exception('Test exception')
		script = cbscript(source, None)
		script.log_lines = []
		script.log = new.instancemethod(mock_log, script, None)
		script.tracebacks = 0
		def mock_log_traceback(self):
			self.tracebacks += 1
		script.log_traceback = new.instancemethod(mock_log_traceback, script, None)
		script.compile_all = new.instancemethod(bad_compile, script, None)
		
		script.try_to_compile()
		self.assertEqual(script.log_lines, [
			'Compiling unittest...',
			'Compiler encountered unexpected error during compilation:\x07'
		])
		self.assertEqual(script.tracebacks, 1)
		
	def test_cbscript_compile_all(self):
		source = mock_source_file()
		
		parsed = {}
		parsed['scale'] = 100
		parsed['assignments'] = [block_tag_block(0, 'test_tag', ['test_block'])]
		parsed['sections'] = [
			('macro', 'test_macro', [], [], []),
			('template_function', 'test_template_function', [], [], []),
			('function', 'reset', [], [], [scoreboard_assignment_block(0, (('Var', ('Global', 'test_var')), '=', func_expr(function_call_block(0, 'rand', [num_expr(5)]))))]),
			('clock', 'test_clock', [], [] ,[]),
		]
		parsed['dir'] = 'test_dir'
		parsed['desc'] = 'test description'
		
		script = cbscript(source, lambda t: ('program', parsed))
		def mock_create_world(self, dir, namespace):
			world = mock_mcworld(dir, namespace)
			self.mock_world = world
			return world
		script.create_world = new.instancemethod(mock_create_world, script, None)
		
		self.assertTrue(script.compile_all())
		world = script.mock_world
		self.assertEqual(world.functions, ['reset', 'test_clock'])
		self.assertEqual(world.clocks, ['test_clock'])
		self.assertEqual(world.tags, ['test_tag'])
		self.assertEqual(world.desc, 'test description')
		self.assertTrue(world.written)
		self.assertTrue('test_var' in script.global_context.objectives)
		self.assertEqual(script.global_context.get_reset_function().commands, [
			'scoreboard objectives add test_var dummy',
			'kill @e[type=minecraft:armor_stand,name=RandBasis,scores={RVunittest=0..}]', 
			'scoreboard objectives add RVunittest dummy', 
			'summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}', 
			'scoreboard players add @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1', 
			'summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}', 
			'scoreboard players add @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1', 
			'summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}', 
			'scoreboard players add @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1', 
			'summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}', 
			'scoreboard players add @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1', 
			'summon minecraft:armor_stand ~ ~ ~ {CustomName:"\\"RandBasis\\"", "Invulnerable":1b, "Invisible":1b, "Marker":1b, "NoGravity":1b}', 
			'scoreboard players add @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1', 
			'scoreboard players remove @e[type=minecraft:armor_stand,name=RandBasis] RVunittest 1',
			'scoreboard objectives add res_scratch0 dummy', 
			'scoreboard players set Global res_scratch0 0', 
			'scoreboard players operation Global res_scratch0 += @e[type=minecraft:armor_stand,limit=1,sort=random,scores={RVunittest=..4}] RVunittest', 
			'scoreboard players operation Global test_var = Global res_scratch0', 
		])
		
	def test_tellraw_get_properties_text(self):
		properties = {
			'color': 'red',
			'bold': True,
			'underlined': True,
			'italic': True,
			'strikethrough': True
		}
		self.assertEqual(tellraw.getPropertiesText(properties), ',"color":"red","bold":true,"underlined":true,"italic":true,"strikethrough":true')
		
		properties = {
			'color': None,
			'bold': False,
			'underlined': False,
			'italic': False,
			'strikethrough': False
		}
		self.assertEqual(tellraw.getPropertiesText(properties), '')
		
	def test_tellraw_format_json_text(self):
		func = mock_mcfunction()
		
		self.assertEqual(
			tellraw.formatJsonText(func, 'test'),
			'["",{"text":"test"}]'
		)
		
		self.assertEqual(
			tellraw.formatJsonText(func, '{rtest'),
			'["",{"text":"test","color":"dark_red"}]'
		)
		
		self.assertEqual(
			tellraw.formatJsonText(func, '[test text](/test_command)'),
			'["",{"text":"test text","clickEvent":{"action":"run_command","value":"/test_command"}}]'
		)
		
		self.assertEqual(
			tellraw.formatJsonText(func, '(global_var)'),
			'["",{"score":{"name":"Global","objective":"global_var"}}]'
		)
		
		self.assertEqual(
			tellraw.formatJsonText(func, '(@test_selector.test_var)'),
			'["",{"score":{"name":"@s","objective":"test_scratch1"}}]'
		)
		
		with self.assertRaises(SyntaxError):
			tellraw.formatJsonText(func, '(a.b.c)')
		
		self.assertEqual(
			tellraw.formatJsonText(func, '(@test_selector[])'),
			'["",{"selector":"@test_selector[]"}]'
		)
		
		with self.assertRaises(SyntaxError):
			tellraw.formatJsonText(func, 'test () text'),
		
		self.assertEqual(
			tellraw.formatJsonText(func, '[link](http://sethbling.com)'),
			'["",{"text":"link","clickEvent":{"action":"open_url","value":"http://sethbling.com"}}]'
		)
		
		self.assertEqual(
			tellraw.formatJsonText(func, '[link](//suggest_test)'),
			'["",{"text":"link","clickEvent":{"action":"suggest_command","value":"/suggest_test"}}]'
		)
		
	def test_tellraw_parse_text_formatting(self):
		self.assertEqual(
			tellraw.parseTextFormatting('\('),
			[('(', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('a['),
			[('a', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('a{'),
			[('a', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('[formatted]test'),
			[
				(('formatted', None), {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False}),
				('test', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{r{Utest{-clear'),
			[
				('test', {'color': 'dark_red', 'underlined': True, 'strikethrough': False, 'bold': False, 'italic': False}),
				('clear', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{Utest{uclear'),
			[
				('test', {'color': None, 'underlined': True, 'strikethrough': False, 'bold': False, 'italic': False}),
				('clear', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{Stest{sclear'),
			[
				('test', {'color': None, 'underlined': False, 'strikethrough': True, 'bold': False, 'italic': False}),
				('clear', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{Dtest{dclear'),
			[
				('test', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': True, 'italic': False}),
				('clear', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{Itest{iclear'),
			[
				('test', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': True}),
				('clear', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})
			]
		)
		
		self.assertEqual(
			tellraw.parseTextFormatting('{{'),
			[('{', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})]
		)
		
		with self.assertRaises(SyntaxError):
			tellraw.parseTextFormatting('{+')
		
		self.assertEqual(
			tellraw.parseTextFormatting('\{'),
			[('{', {'color': None, 'underlined': False, 'strikethrough': False, 'bold': False, 'italic': False})]
		)
		
	def test_parser(self):
		mcfunction.line_numbers = []
	
		p = mock_parsed('test1')
		scriptparse.p_parsed_assignment(p)
		self.assertEqual(p[0], ('program', 'test1'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('test2')
		scriptparse.p_parsed_expr(p)
		self.assertEqual(p[0], ('expr', 'test2'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('comments', None, 'dir', None, 'desc', 'scale', 'assignments', 'sections')
		scriptparse.p_program(p)
		self.assertEqual(p[0], {'assignments': 'assignments', 'scale': 'scale', 'sections': 'sections', 'dir': 'dir', 'desc': 'desc'})
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'desc', None)
		scriptparse.p_optdesc(p)
		self.assertEqual(p[0], 'desc')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_optdesc(p)
		self.assertEqual(p[0], 'No Description')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 500, None)
		scriptparse.p_optscale(p)
		self.assertEqual(p[0], 500)
		
		p = mock_parsed(None)
		scriptparse.p_optscale_none(p)
		self.assertEqual(p[0], 1000)
		
		p = mock_parsed('section', None, ['sections'])
		scriptparse.p_sections_multiple(p)
		self.assertEqual(p[0], ['section', 'sections'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_sections_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed(['comment'], ('type', 'name', ['template_params'], ['params'], ['lines']))
		scriptparse.p_section_commented(p)
		p_type, p_name, p_template_params, p_params, p_lines = p[0]
		self.assertEqual(p_type, 'type')
		self.assertEqual(p_name, 'name')
		self.assertEqual(p_template_params, ['template_params'])
		self.assertEqual(p_params, ['params'])
		self.assertEqual(type(p_lines[0]), comment_block)
		self.assertEqual(p_lines[0].text, '#comment')
		self.assertEqual(p_lines[1], 'lines')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('comment', None, ['comments'])
		scriptparse.p_optcomments(p)
		self.assertEqual(p[0], ['comment', 'comments'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_optcomments_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('section')
		scriptparse.p_section(p)
		self.assertEqual(p[0], 'section')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, 'lines', None)
		scriptparse.p_resetsection(p)
		self.assertEqual(p[0], ('reset', 'reset', [], [], 'lines'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		with self.assertRaises(SyntaxError):
			scriptparse.validate_mcfunction_name('Test')
		scriptparse.validate_mcfunction_name('test')
		
		p = mock_parsed(None, 'id', None, 'lines', None)
		scriptparse.p_clocksection(p)
		self.assertEqual(p[0], ('clock', 'id', [], [], 'lines'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, ['id_list'], None, None, 'lines', None)
		scriptparse.p_functionsection(p)
		self.assertEqual(p[0], ('function', 'id', [], ['id_list'], 'lines'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, ['macro_params'], None, None, ['id_list'], None, None, 'lines', None)
		scriptparse.p_template_function_section(p)
		self.assertEqual(p[0], ('template_function', 'id', ['macro_params'], ['id_list'], 'lines'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, 'id', 'macro_args', None, 'lines', None)
		scriptparse.p_macrosection(p)
		self.assertEqual(p[0], ('macro', 'id', [], 'macro_args', 'lines'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'params', None)
		scriptparse.p_macro_args(p)
		self.assertEqual(p[0], 'params')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_macro_args_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed(None, 'id', None, ['params'])
		scriptparse.p_macro_params(p)
		self.assertEqual(p[0], ['id', 'params'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'macro_id')
		scriptparse.p_macro_params_one(p)
		self.assertEqual(p[0], ['macro_id'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_macro_params_empty(p)
		self.assertEqual(p[0], [])

		p = mock_parsed(None, None)
		scriptparse.p_newlines(p)
		self.assertEqual(p[0], None)
		
		p = mock_parsed(None)
		scriptparse.p_newlines(p)
		self.assertEqual(p[0], None)
		
		p = mock_parsed(None)
		scriptparse.p_optnewlines(p)
		self.assertEqual(p[0], None)
		
		p = mock_parsed('id', None, ['ids'])
		scriptparse.p_id_list(p)
		self.assertEqual(p[0], ['id', 'ids'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id')
		scriptparse.p_id_list_one(p)
		self.assertEqual(p[0], ['id'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_id_list_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('assignment', None, ['assignments'])
		scriptparse.p_optassignments_multiple(p)
		self.assertEqual(p[0], ['assignment', 'assignments'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('comment', None, ['assignments'])
		scriptparse.p_optassignments_comment(p)
		self.assertEqual(p[0], ['assignments'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_optassignments_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('fullselector', None, 'id')
		scriptparse.p_variable_selector(p)
		self.assertEqual(p[0], ('Var', ('fullselector', 'id')))
		
		p = mock_parsed('id')
		scriptparse.p_variable_global(p)
		self.assertEqual(p[0], ('Var', ('Global', 'id')))
		
		p = mock_parsed('id', None, 'idx')
		scriptparse.p_variable_array_const(p)
		self.assertEqual(p[0], ('ArrayConst', ('id', 'idx')))
		
		p = mock_parsed('id', None, 'expr')
		scriptparse.p_variable_array_expr(p)
		self.assertEqual(p[0], ('ArrayExpr', ('id', 'expr')))
		
		p = mock_parsed('#comment')
		scriptparse.p_optcomment(p)
		self.assertEqual(len(p[0]), 1)
		self.assertTrue(type(p[0][0]) is comment_block)
		self.assertEqual(p[0][0].text, '#comment')
		self.assertEqual(mcfunction.get_line(p[0]), 0)

		p = mock_parsed(None)
		scriptparse.p_optcomment_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('codeblock', ['optcomment'], None, ['lines'])
		scriptparse.p_blocklist_multiple(p)
		self.assertEqual(p[0], ['optcomment', 'codeblock', 'lines'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None)
		scriptparse.p_blocklist_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('#comment')
		scriptparse.p_block_comment(p)
		self.assertTrue(type(p[0]) is comment_block)
		self.assertEqual(p[0].text, '#comment')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('command')
		scriptparse.p_block_command(p)
		self.assertTrue(type(p[0]) is command_block)
		self.assertEqual(p[0].text, 'command')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'selector', 'coords')
		scriptparse.p_block_move(p)
		self.assertTrue(type(p[0]) is move_block)
		self.assertEqual(p[0].selector, 'selector')
		self.assertEqual(p[0].coords, 'coords')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, 'id', None, 'python', None, 'lines', None)
		scriptparse.p_block_for(p)
		self.assertTrue(type(p[0]) is python_for_block)
		self.assertEqual(p[0].id, 'id')
		self.assertEqual(p[0].code, 'python')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'var', None, 'lines', None)
		scriptparse.p_execute_as_id_global(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsId',('var', None))])
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'var', None, '@id', None, None, 'lines', None)
		scriptparse.p_execute_as_id_type_global(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsId',('var', '@id'))])
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'var', None, 'line')
		scriptparse.p_execute_as_id_do_global(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsId',('var', None))])
		self.assertEqual(p[0].sub, ['line'])
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'var', None, '@id', None, None, 'line')
		scriptparse.p_execute_as_id_do_type_global(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsId',('var', '@id'))])
		self.assertEqual(p[0].sub, ['line'])
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'create', None, 'lines', None)
		scriptparse.p_execute_as_create(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsCreate','create')])
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'create', None, 'line')
		scriptparse.p_execute_as_create_do(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, [('AsCreate','create')])
		self.assertEqual(p[0].sub, ['line'])
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('items', None, 'lines', None)
		scriptparse.p_execute_chain(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, 'items')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('items', None, 'line')
		scriptparse.p_execute_chain_inline(p)
		self.assertTrue(type(p[0]) is execute_block)
		self.assertEqual(p[0].exec_items, 'items')
		self.assertEqual(p[0].sub, ['line'])
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('item')
		scriptparse.p_execute_items_one(p)
		self.assertEqual(p[0], ['item'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('item', ['items'])
		scriptparse.p_execute_items(p)
		self.assertEqual(p[0], ['item', 'items'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'conditions')
		scriptparse.p_execute_if_condition(p)
		self.assertEqual(p[0], ('If', 'conditions'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'conditions')
		scriptparse.p_execute_unless_condition(p)
		self.assertEqual(p[0], ('Unless', 'conditions'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'fullselector')
		scriptparse.p_execute_as(p)
		self.assertEqual(p[0], ('As', 'fullselector'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'fullselector')
		scriptparse.p_execute_rotated(p)
		self.assertEqual(p[0], ('Rotated', 'fullselector'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'relcoords')
		scriptparse.p_execute_facing_coords(p)
		self.assertEqual(p[0], ('FacingCoords', 'relcoords'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'fullselector')
		scriptparse.p_execute_facing_entity(p)
		self.assertEqual(p[0], ('FacingEntity', 'fullselector'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		for axes in ['x','y','z','xy','xz','yz','xyz']:
			p = mock_parsed(None, axes)
			scriptparse.p_execute_align(p)
			self.assertEqual(p[0], ('Align', axes))
			self.assertEqual(mcfunction.get_line(p[0]), 0)
			
		p = mock_parsed(None, '')
		with self.assertRaises(SyntaxError):
			scriptparse.p_execute_align(p)
		
		p = mock_parsed(None, 'fullselector')
		scriptparse.p_execute_at_selector(p)
		self.assertEqual(p[0], ('At', ('fullselector', None)))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'relcoords')
		scriptparse.p_execute_at_relcoords(p)
		self.assertEqual(p[0], ('At', (None, 'relcoords')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'fullselector', 'relcoords')
		scriptparse.p_execute_at_selector_relcoords(p)
		self.assertEqual(p[0], ('At', ('fullselector', 'relcoords')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'vector_expr')
		scriptparse.p_execute_at_vector(p)
		self.assertEqual(p[0], ('AtVector', (None, 'vector_expr')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, '200', None, 'vector_expr')
		scriptparse.p_execute_at_vector_scale(p)
		self.assertEqual(p[0], ('AtVector', ('200', 'vector_expr')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'overworld')
		scriptparse.p_execute_in_dimension(p)
		self.assertEqual(p[0], ('In', 'overworld'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, '@id', None, 'lines', None)
		scriptparse.p_for_selector(p)
		self.assertTrue(type(p[0]) is for_selector_block)
		self.assertEqual(p[0].id, 'id')
		self.assertEqual(p[0].selector, '@id')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('condition')
		scriptparse.p_conditions_one(p)
		self.assertEqual(p[0], ['condition'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('condition', None, ['conditions'])
		scriptparse.p_conditions(p)
		self.assertEqual(p[0], ['condition', 'conditions'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', None, 'fullselector')
		scriptparse.p_condition_pointer(p)
		self.assertEqual(p[0], ('pointer', ('var', 'fullselector')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('fullselector', None, 'var')
		scriptparse.p_condition_pointer_reversed(p)
		self.assertEqual(p[0], ('pointer', ('var', 'fullselector')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('fullselector')
		scriptparse.p_condition_fullselector(p)
		self.assertEqual(p[0], ('selector', 'fullselector'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '<', 'comp')
		scriptparse.p_condition_score(p)
		self.assertEqual(p[0], ('score', ('var', '<', 'comp')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '==', 'comp')
		scriptparse.p_condition_score(p)
		self.assertEqual(p[0], ('score', ('var', '=', 'comp')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('v1', '==', 'v2')
		scriptparse.p_condition_vector_equality(p)
		self.assertEqual(p[0], ('vector_equality', ('v1', 'v2')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var')
		scriptparse.p_condition_bool(p)
		self.assertEqual(p[0], ('score', ('var', '>', ('num', '0'))))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'var')
		scriptparse.p_condition_not_bool(p)
		self.assertEqual(p[0], ('score', ('var', '<=', ('num', '0'))))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'relcoords', 'id')
		scriptparse.p_condition_block(p)
		self.assertEqual(p[0], ('block', ('relcoords', 'id')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('100')
		scriptparse.p_comparison_num(p)
		self.assertEqual(p[0], ('num', '100'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var')
		scriptparse.p_comparison_global(p)
		self.assertEqual(p[0], ('score', 'var'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'code', None, 'lines', None)
		scriptparse.p_block_if_command(p)
		self.assertTrue(type(p[0]) is python_if_block)
		self.assertEqual(p[0].code, 'code')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].else_sub, None)
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'code', None, 'lines', None, None, 'else_lines', None)
		scriptparse.p_block_ifelse_command(p)
		self.assertTrue(type(p[0]) is python_if_block)
		self.assertEqual(p[0].code, 'code')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].else_sub, 'else_lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'conditions', None, 'lines', None)
		scriptparse.p_block_while(p)
		self.assertTrue(type(p[0]) is while_block)
		self.assertEqual(p[0].exec_items, [('If', 'conditions')])
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'conditions', ['items'], None, 'lines', None)
		scriptparse.p_block_while_execute(p)
		self.assertTrue(type(p[0]) is while_block)
		self.assertEqual(p[0].exec_items, [('If', 'conditions'), 'items'])
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, 'from', None, 'to', None, 'by', None, 'lines', None)
		scriptparse.p_block_for_index_by(p)
		self.assertTrue(type(p[0]) is for_index_block)
		self.assertEqual(p[0].var, 'id')
		self.assertEqual(p[0].fr, 'from')
		self.assertEqual(p[0].to, 'to')
		self.assertEqual(p[0].by, 'by')
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, 'from', None, 'to', None, 'lines', None)
		scriptparse.p_block_for_index(p)
		self.assertTrue(type(p[0]) is for_index_block)
		self.assertEqual(p[0].var, 'id')
		self.assertEqual(p[0].fr, 'from')
		self.assertEqual(p[0].to, 'to')
		self.assertEqual(p[0].by, None)
		self.assertEqual(p[0].sub, 'lines')
		self.assertEqual(p[0].line, 0)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'expr', None, 'cases', None)
		scriptparse.p_switch(p)
		self.assertTrue(type(p[0]) is switch_block)
		self.assertEqual(p[0].expr, 'expr')
		self.assertEqual(p[0].cases_raw, 'cases')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('case')
		scriptparse.p_cases_one(p)
		self.assertEqual(p[0], ['case'])
		
		p = mock_parsed('case', None, ['cases'])
		scriptparse.p_cases_multiple(p)
		self.assertEqual(p[0], ['case', 'cases'])
		
		p = mock_parsed(None, '100', None, 'lines', None)
		scriptparse.p_switch_case_single(p)
		self.assertEqual(p[0], ('range', ('100', '100', 'lines')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, '100', None, '200', None, 'lines', None)
		scriptparse.p_switch_case_range(p)
		self.assertEqual(p[0], ('range', ('100', '200', 'lines')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, 'id', None, 'code', None, 'lines', None)
		scriptparse.p_switch_case_python(p)
		self.assertEqual(p[0], ('python', ('id', 'code', 'lines')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'fullselector', 'text')
		scriptparse.p_block_tell(p)
		self.assertTrue(type(p[0]) is tell_block)
		self.assertEqual(p[0].selector, 'fullselector')
		self.assertEqual(p[0].unformatted, 'text')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('title', 'selector', 'text')
		scriptparse.p_block_title(p)
		self.assertTrue(type(p[0]) is title_block)
		self.assertEqual(p[0].subtype, 'title')
		self.assertEqual(p[0].selector, 'selector')
		self.assertEqual(p[0].times, None)
		self.assertEqual(p[0].unformatted, 'text')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('subtitle', 'selector', '1', '2', '3', 'text')
		scriptparse.p_block_title_times(p)
		self.assertTrue(type(p[0]) is title_block)
		self.assertEqual(p[0].subtype, 'subtitle')
		self.assertEqual(p[0].selector, 'selector')
		self.assertEqual(p[0].times, ('1', '2', '3'))
		self.assertEqual(p[0].unformatted, 'text')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('call')
		scriptparse.p_block_function_call(p)
		self.assertEqual(p[0], 'call')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(('var', 'op', 'expr'))
		scriptparse.p_block_math(p)
		self.assertTrue(type(p[0]) is scoreboard_assignment_block)
		self.assertEqual(p[0].var, 'var')
		self.assertEqual(p[0].op, 'op')
		self.assertEqual(p[0].expr, 'expr')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('selector_assignment')
		scriptparse.p_block_selector_assignment(p)
		self.assertEqual(p[0], 'selector_assignment')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('100')
		scriptparse.p_integer(p)
		self.assertEqual(p[0], '100')
		
		p = mock_parsed(None, '100')
		scriptparse.p_integer_minus(p)
		self.assertEqual(p[0], '-100')
		
		p = mock_parsed('100')
		scriptparse.p_number_integer(p)
		self.assertEqual(p[0], '100')
		
		p = mock_parsed('1.0')
		scriptparse.p_float_val(p)
		self.assertEqual(p[0], '1.0')
		
		p = mock_parsed(None, '1.0')
		scriptparse.p_float_val_minus(p)
		self.assertEqual(p[0], '-1.0')
		
		func = mock_mcfunction()
		p = mock_parsed('1.0')
		scriptparse.p_virtualnumber_literal(p)
		self.assertEqual(p[0].get_value(func), 1.0)
		
		func = mock_mcfunction()
		func.dollarid['test'] = 5
		p = mock_parsed(None, 'test')
		scriptparse.p_virtualnumber_symbol(p)
		self.assertEqual(p[0].get_value(func), 5)
		
		func = mock_mcfunction()
		func.dollarid['test2'] = 10
		p = mock_parsed(None, None, 'test2')
		scriptparse.p_virtualnumber_symbol_negative(p)
		self.assertEqual(p[0].get_value(func), -10)
		
		func = mock_mcfunction()
		func.dollarid['test3'] = 10
		p = mock_parsed(None, '5 + test3')
		scriptparse.p_virtualnumber_interpreted(p)
		self.assertEqual(p[0].get_value(func), 15)

		func = mock_mcfunction()
		p = mock_parsed('test string')
		scriptparse.p_virtualnumber_string(p)
		self.assertEqual(p[0].get_value(func), 'test string')

		
		p = mock_parsed('100')
		scriptparse.p_virtualinteger_literal(p)
		self.assertEqual(p[0], '100')
		
		p = mock_parsed(None, 'test')
		scriptparse.p_virtualinteger_symbol(p)
		self.assertEqual(p[0], '$test')
		
		p = mock_parsed(None, None, 'id', None, 'blocks', None)
		scriptparse.p_blocktag(p)
		self.assertTrue(type(p[0]) is block_tag_block)
		self.assertEqual(p[0].name, 'id')
		self.assertEqual(p[0].blocks, 'blocks')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('block', None, ['blocks'])
		scriptparse.p_block_list(p)
		self.assertEqual(p[0], ['block', 'blocks'])
		
		p = mock_parsed('block')
		scriptparse.p_block_list_one(p)
		self.assertEqual(p[0], ['block'])
		
		p = mock_parsed('id', None, 'fullselector')
		scriptparse.p_selector_assignment(p)
		self.assertTrue(type(p[0]) is selector_assignment_block)
		self.assertEqual(p[0].id, 'id')
		self.assertEqual(p[0].fullselector, 'fullselector')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, 'fullselector', None, 'def', None)
		scriptparse.p_selector_define(p)
		self.assertTrue(type(p[0]) is selector_definition_block)
		self.assertEqual(p[0].id, 'id')
		self.assertEqual(p[0].fullselector, 'fullselector')
		self.assertEqual(p[0].items, 'def')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('item', None, ['items'])
		scriptparse.p_selector_definition(p)
		self.assertEqual(p[0], ['item', 'items'])
		
		p = mock_parsed(None)
		scriptparse.p_selector_definition_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed(None, 'data') 
		scriptparse.p_selector_item_tag(p)
		self.assertEqual(p[0], ('Tag', 'data'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, 'path', 'type', 'scale') 
		scriptparse.p_selector_item_path_scale(p)
		self.assertEqual(p[0], ('Path', ('id', 'path', 'type', 'scale')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, 'path', 'type') 
		scriptparse.p_selector_item_path(p)
		self.assertEqual(p[0], ('Path', ('id', 'path', 'type', None)))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, None, 'path', 'type', 'scale') 
		scriptparse.p_selector_item_vector_path_scale(p)
		self.assertEqual(p[0], ('VectorPath', ('id', 'path', 'type', 'scale')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, None, 'path', 'type') 
		scriptparse.p_selector_item_vector_path(p)
		self.assertEqual(p[0], ('VectorPath', ('id', 'path', 'type', None)))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('function') 
		scriptparse.p_selector_item_method(p)
		self.assertEqual(p[0], ('Method', 'function'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id') 
		scriptparse.p_data_path_id(p)
		self.assertEqual(p[0], 'id')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, '1', None) 
		scriptparse.p_data_path_array(p)
		self.assertEqual(p[0], 'id[1]')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('a', None, 'b') 
		scriptparse.p_data_path_multi(p)
		self.assertEqual(p[0], 'a.b')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('byte') 
		scriptparse.p_data_type(p)
		self.assertEqual(p[0], 'byte')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, '1', None) 
		scriptparse.p_array_definition(p)
		self.assertTrue(type(p[0]) is array_definition_block)
		self.assertEqual(p[0].name, 'id')
		self.assertEqual(p[0].from_val, '0')
		self.assertEqual(p[0].to_val, '1')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None, '1', None, '2', None) 
		scriptparse.p_array_definition_range(p)
		self.assertTrue(type(p[0]) is array_definition_block)
		self.assertEqual(p[0].name, 'id')
		self.assertEqual(p[0].from_val, '1')
		self.assertEqual(p[0].to_val, '2')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('create_block') 
		scriptparse.p_block_create(p)
		self.assertEqual(p[0], 'create_block')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', 'relcoords') 
		scriptparse.p_create(p)
		self.assertTrue(type(p[0]) is create_block)
		self.assertEqual(p[0].atid, 'id')
		self.assertEqual(p[0].relcoords, 'relcoords')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id') 
		func = mock_mcfunction()
		scriptparse.p_create_nocoords(p)
		self.assertTrue(type(p[0]) is create_block)
		self.assertEqual(p[0].atid, 'id')
		self.assertEqual(p[0].relcoords.get_value(func), '~ ~ ~')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('qualifiers', None, 'qualifier') 
		scriptparse.p_qualifiers_multiple(p)
		self.assertEqual(p[0], 'qualifiers,qualifier')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('qualifier') 
		scriptparse.p_qualifiers_one(p)
		self.assertEqual(p[0], 'qualifier')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_qualifiers(p)
		self.assertEqual(p[0], '')
		
		p = mock_parsed('100') 
		scriptparse.p_qualifier_integer(p)
		self.assertEqual(p[0], '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', '<=', 'id2') 
		scriptparse.p_qualifier_binop(p)
		self.assertEqual(p[0], 'id<=id2')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', '=', '100', '.', '.', '200') 
		scriptparse.p_qualifier_builtin(p)
		self.assertEqual(p[0], 'id=100..200')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', '=') 
		scriptparse.p_qualifier_empty(p)
		self.assertEqual(p[0], 'id=')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', '=', '!', 'id2') 
		scriptparse.p_qualifier_is_not(p)
		self.assertEqual(p[0], 'id=!id2')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id') 
		scriptparse.p_qualifier_is(p)
		self.assertEqual(p[0], 'id')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('not', 'id') 
		scriptparse.p_qualifier_not(p)
		self.assertEqual(p[0], 'not id')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id') 
		scriptparse.p_fullselector_symbol(p)
		self.assertEqual(p[0], '@id[]')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, 'qualifiers', None) 
		scriptparse.p_fullselector_symbol(p)
		self.assertEqual(p[0], '@id[qualifiers]')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(const_number('100'))
		func = mock_mcfunction()
		scriptparse.p_relcoord_number(p)
		self.assertEqual(p[0].get_value(func), '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, const_number('100')) 
		func = mock_mcfunction()
		scriptparse.p_relcoord_relnumber(p)
		self.assertEqual(p[0].get_value(func), '~100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		func = mock_mcfunction()
		scriptparse.p_relcoord_relzero(p)
		self.assertEqual(p[0].get_value(func), '~')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('^', const_number('100')) 
		func = mock_mcfunction()
		scriptparse.p_localcoord_localnumber(p)
		self.assertEqual(p[0].get_value(func), '^100')
		
		p = mock_parsed(relcoord('', const_number('1')), relcoord('', const_number('2')), relcoord('', const_number('3')))
		func = mock_mcfunction()
		scriptparse.p_relcoords(p)
		self.assertEqual(p[0].get_value(func), '1 2 3')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'expr') 
		scriptparse.p_return_expression(p)
		self.assertEqual(p[0], (('Var', ('Global', 'ReturnValue')), '=', 'expr'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '+=', 'expr') 
		scriptparse.p_assignment(p)
		self.assertEqual(p[0], ('var', '+=', 'expr'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '++') 
		scriptparse.p_assignment_unary_default(p)
		var, op, expr = p[0]
		self.assertEqual(var, 'var')
		self.assertEqual(op, '+=')
		self.assertTrue(type(expr) is num_expr)
		self.assertEqual(expr.const_value(), '1')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '=', 'selector') 
		scriptparse.p_assignment_selector_global(p)
		var, op, expr = p[0]
		self.assertEqual(var, 'var')
		self.assertEqual(op, '=')
		self.assertTrue(type(expr) is selector_expr)
		self.assertEqual(expr.selector, 'selector')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '=', 'create') 
		scriptparse.p_assignment_create(p)
		var, op, expr = p[0]
		self.assertEqual(var, 'var')
		self.assertEqual(op, '=')
		self.assertTrue(type(expr) is create_expr)
		self.assertEqual(expr.create_block, 'create')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '+=', 'expr') 
		scriptparse.p_vector_assignment_vector(p)
		self.assertTrue(type(p[0]) is vector_assignment_block)
		self.assertEqual(p[0].var, 'var')
		self.assertEqual(p[0].op, '+=')
		self.assertEqual(p[0].expr, 'expr')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('var', '+=', 'expr') 
		scriptparse.p_vector_assignment_scalar(p)
		self.assertTrue(type(p[0]) is vector_assignment_scalar_block)
		self.assertEqual(p[0].var, 'var')
		self.assertEqual(p[0].op, '+=')
		self.assertEqual(p[0].expr, 'expr')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None) 
		scriptparse.p_vector_var_id(p)
		self.assertEqual(p[0], ('VAR_ID', 'id'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('selector', None, None, 'id', None) 
		scriptparse.p_vector_var_sel_id(p)
		self.assertEqual(p[0], ('SEL_VAR_ID', ('selector', 'id')))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'a', None, 'b', None, 'c', None) 
		scriptparse.p_vector_var_components(p)
		self.assertEqual(p[0], ('VAR_COMPONENTS', ['a', 'b', 'c']))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('a', None, 'b') 
		scriptparse.p_expr_dot(p)
		self.assertTrue(type(p[0]) is dot_expr)
		self.assertEqual(p[0].lhs, 'a')
		self.assertEqual(p[0].rhs, 'b')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('100') 
		scriptparse.p_expr_number(p)
		self.assertTrue(type(p[0]) is num_expr)
		self.assertEqual(p[0].val, '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_expr_scale(p)
		self.assertTrue(type(p[0]) is scale_expr)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id') 
		scriptparse.p_expr_variable(p)
		self.assertTrue(type(p[0]) is selvar_expr)
		self.assertEqual(p[0].sel, 'Global')
		self.assertEqual(p[0].var, 'id')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, '100', None) 
		scriptparse.p_expr_array_const(p)
		self.assertTrue(type(p[0]) is arrayconst_expr)
		self.assertEqual(p[0].name, 'id')
		self.assertEqual(p[0].idx, '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, 'expr', None) 
		scriptparse.p_expr_array_expr(p)
		self.assertTrue(type(p[0]) is arrayexpr_expr)
		self.assertEqual(p[0].name, 'id')
		self.assertEqual(p[0].idx_expr, 'expr')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('selector', None, 'id') 
		scriptparse.p_expr_selector_variable(p)
		self.assertTrue(type(p[0]) is selvar_expr)
		self.assertEqual(p[0].sel, 'selector')
		self.assertEqual(p[0].var, 'id')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('call') 
		scriptparse.p_expr_function(p)
		self.assertTrue(type(p[0]) is func_expr)
		self.assertEqual(p[0].function_call, 'call')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'group', None) 
		scriptparse.p_expr_group(p)
		self.assertEqual(p[0], 'group')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('-', num_expr(100)) 
		scriptparse.p_expr_unary(p)
		self.assertTrue(type(p[0]) is num_expr)
		self.assertEqual(p[0].val, '-100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('-', scale_expr()) 
		scriptparse.p_expr_unary(p)
		self.assertTrue(type(p[0]) is unary_expr)
		self.assertEqual(p[0].type, '-')
		self.assertTrue(type(p[0].expr) is scale_expr)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'group', None) 
		scriptparse.p_vector_expr_paren(p)
		self.assertEqual(p[0], 'group')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'a', None, 'b', None, 'c', None) 
		scriptparse.p_vector_expr_vector_triplet(p)
		self.assertTrue(type(p[0]) is vector_expr)
		self.assertEqual(p[0].exprs, ('a', 'b', 'c'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', None) 
		scriptparse.p_vector_expr_vector_unit(p)
		self.assertTrue(type(p[0]) is vector_var_expr)
		self.assertEqual(p[0].vector_id, ('id'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('selector', None, None, 'id', None) 
		scriptparse.p_vector_expr_selector_vector(p)
		self.assertTrue(type(p[0]) is sel_vector_var_expr)
		self.assertEqual(p[0].sel, ('selector'))
		self.assertEqual(p[0].id, ('id'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('expr1', '+', 'expr2') 
		scriptparse.p_vector_expr_binop_vector(p)
		self.assertTrue(type(p[0]) is vector_binop_vector_expr)
		self.assertEqual(p[0].lhs, ('expr1'))
		self.assertEqual(p[0].op, ('+'))
		self.assertEqual(p[0].rhs, ('expr2'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('expr1', '+', 'expr2') 
		scriptparse.p_vector_expr_binop_scalar(p)
		self.assertTrue(type(p[0]) is vector_binop_scalar_expr)
		self.assertEqual(p[0].lhs, ('expr1'))
		self.assertEqual(p[0].op, ('+'))
		self.assertEqual(p[0].rhs, ('expr2'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('expr1', '+', 'expr2') 
		scriptparse.p_vector_expr_binop_scalar_reversed(p)
		self.assertTrue(type(p[0]) is vector_binop_scalar_expr)
		self.assertEqual(p[0].lhs, ('expr2'))
		self.assertEqual(p[0].op, ('+'))
		self.assertEqual(p[0].rhs, ('expr1'))
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('-', 'expr') 
		scriptparse.p_vector_expr_negative(p)
		self.assertTrue(type(p[0]) is vector_binop_scalar_expr)
		self.assertEqual(p[0].lhs, ('expr'))
		self.assertEqual(p[0].op, ('*'))
		self.assertTrue(type(p[0].rhs) is num_expr)
		self.assertEqual(p[0].rhs.const_value(), '-1')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_vector_expr_here(p)
		self.assertTrue(type(p[0]) is vector_here_expr)
		self.assertEqual(p[0].scale, None)
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, None, '100', None) 
		scriptparse.p_vector_expr_here_scale(p)
		self.assertTrue(type(p[0]) is vector_here_expr)
		self.assertEqual(p[0].scale, '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('id', None, 'exprs', None) 
		scriptparse.p_function_call(p)
		self.assertTrue(type(p[0]) is function_call_block)
		self.assertEqual(p[0].dest, 'id')
		self.assertEqual(p[0].args, 'exprs')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('selector', None, 'id', None, 'exprs', None) 
		scriptparse.p_method_call(p)
		self.assertTrue(type(p[0]) is method_call_block)
		self.assertEqual(p[0].selector, 'selector')
		self.assertEqual(p[0].dest, 'id')
		self.assertEqual(p[0].params, 'exprs')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(['exprs'], None, 'expr') 
		scriptparse.p_exprlist_multiple(p)
		self.assertEqual(p[0], ['exprs', 'expr'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('expr') 
		scriptparse.p_exprlist_single(p)
		self.assertEqual(p[0], ['expr'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_exprlist_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('id', None, 'macro_params', None, None, 'function_params', None) 
		scriptparse.p_template_function_call(p)
		self.assertTrue(type(p[0]) is template_function_call_block)
		self.assertEqual(p[0].function, 'id')
		self.assertEqual(p[0].template_args, 'macro_params')
		self.assertEqual(p[0].args, 'function_params')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'id', 'macro_params') 
		scriptparse.p_macro_call(p)
		self.assertTrue(type(p[0]) is macro_call_block)
		self.assertEqual(p[0].macro, 'id')
		self.assertEqual(p[0].args, 'macro_params')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None, 'params', None) 
		scriptparse.p_macro_call_args(p)
		self.assertEqual(p[0], 'params')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_macro_call_args_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('param', None, ['params']) 
		scriptparse.p_macro_call_params(p)
		self.assertEqual(p[0], ['param', 'params'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed('param') 
		scriptparse.p_macro_call_params_one(p)
		self.assertEqual(p[0], ['param'])
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
		p = mock_parsed(None) 
		scriptparse.p_macro_call_params_empty(p)
		self.assertEqual(p[0], [])
		
		p = mock_parsed('100') 
		scriptparse.p_macro_call_param_number(p)
		self.assertEqual(p[0], '100')
		self.assertEqual(mcfunction.get_line(p[0]), 0)
		
	def test_mcfunction_get_modifiable_id(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		id = func.get_modifiable_id('test', 'assign')
		self.assertEqual(id, 'assign')
		self.assertEqual(func.commands, ['scoreboard players operation Global assign = Global test'])
		
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		id = func.get_modifiable_id('test', 'test')
		self.assertEqual(id, 'test')
		self.assertEqual(func.commands, [])
		
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		id = func.get_modifiable_id('test', None)
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(func.commands, ['scoreboard players operation Global test_scratch1 = Global test'])
		
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		id = func.get_modifiable_id('test_scratch1', None)
		self.assertEqual(id, 'test_scratch1')
		self.assertEqual(func.commands, [])
		
	def test_mcfunction_evaluate_params(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		self.assertTrue(func.evaluate_params([num_expr(1)]))
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_scratch1 1',
			'scoreboard players operation Global Param0 = Global test_scratch1'
		])		
		
	def test_mcfunction_get_variable_non_single_entity(self):
		env = mock_environment()
		sel = mock_selector_definition()
		sel.paths['test_path'] = 'path', 'float', 100
		sel.base_name = '@e'
		sel.is_single_entity = False
		env.selectors['test_selector'] = sel
		env.selector_definitions['@test_selector'] = sel
		func = mcfunction.mcfunction(env)
		
		var = 'Var', ('@test_selector', 'test_path')
		
		with self.assertRaises(Exception):
			var_ret = func.get_variable(var, True)
	
	def test_mcfunction_get_variable_path(self):
		env = mock_environment()
		sel = mock_selector_definition()
		sel.paths['test_path'] = 'path', 'float', 100
		sel.base_name = '@s'
		sel.is_single_entity = True
		env.selectors['test_selector'] = sel
		env.selector_definitions['@test_selector'] = sel
		func = mcfunction.mcfunction(env)
		
		var = 'Var', ('@test_selector', 'test_path')
		
		var_ret = func.get_variable(var, True)
		self.assertEqual(var_ret, var[1])
		self.assertEqual(func.commands, ['execute store result score @test_selector test_path run data get entity @test_selector path 100'])
		
	def test_mcfunction_get_variable_arrayconst(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		var = 'ArrayConst', ('test_array', '1')
		var_ret = func.get_variable(var, True)
		
		self.assertEqual(var_ret, ('Global', 'test_array1'))
		self.assertEqual(func.commands, [])
		
	def test_mcfunction_get_variable_arrayexpr(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		env.arrays['test_array'] = (0, 10)
		
		var = 'ArrayExpr', ('test_array', num_expr(1))
		var_ret = func.get_variable(var, True)
		
		self.assertEqual(var_ret, ('Global', 'test_arrayVal'))
		self.assertEqual(func.commands, [
			'scoreboard players set Global test_arrayIdx 1',
			'function test_namespace:array_test_array_get'
		])
		
	def test_mcfunction_get_variable_arrayexpr_noarray(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		var = 'ArrayExpr', ('test_array', num_expr(1))
		with self.assertRaises(NameError):
			var_ret = func.get_variable(var, True)
			
	def test_mcfunction_set_variable_var(self):
		env = mock_environment()
		sel = mock_selector_definition()
		sel.paths['test_path'] = 'path', 'float', 100
		sel.base_name = '@s'
		sel.is_single_entity = True
		env.selectors['test_selector'] = sel
		env.selector_definitions['@test_selector'] = sel
		func = mcfunction.mcfunction(env)
		
		var = 'Var', ('@test_selector', 'test_path')
		
		func.set_variable(var)
		self.assertEqual(func.commands, ['execute store result entity @test_selector path float 0.01 run scoreboard players get @test_selector test_path'])
		
	def test_mcfunction_set_variable_arrayexpr(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		var = ('ArrayExpr', ('test_array', num_expr(1)))
		
		func.set_variable(var)
		self.assertEqual(func.commands, ['function test_namespace:array_test_array_set'])
		
	def test_mcfunction_get_if_chain_selector(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'selector', '@p'
		chain = func.get_if_chain([condition])
		
		self.assertEqual(chain, 'if entity @p ')
		
	def test_mcfunction_get_if_chain_score_num(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		for op, match in [
			('>', '2..'),
			('<', '..0'),
			('>=', '1..'),
			('<=', '..1'),
			('=', '1..1'),
		]:				
			condition = 'score', (('Var', ('@test_selector', 'test_var')), op, ('num', 1))
			chain = func.get_if_chain([condition])
		
			self.assertEqual(chain, 'if score @test_selector test_var matches {} '.format(match))
		
	def test_mcfunction_get_if_chain_score_var(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'score', (('Var', ('@test_selector', 'test_var')), '>', ('score', ('Var', ('@test_selector2', 'test_var2'))))
		chain = func.get_if_chain([condition])
	
		self.assertEqual(chain, 'if score @test_selector test_var > @test_selector2 test_var2 ')
		
	def test_mcfunction_get_if_chain_score_bad_comparison_type(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'score', (('Var', ('@test_selector', 'test_var')), '>', ('bad', None))
		with self.assertRaises(ValueError):
			func.get_if_chain([condition])
			
	def test_mcfunction_get_if_chain_pointer(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'pointer', (('Var', ('@test_selector', 'test_var')), '@test_selector2')
		chain = func.get_if_chain([condition])
		
		self.assertEqual(chain, 'if score @test_selector test_var = @test_selector2 _id ')

	def test_mcfunction_get_if_chain_vector_equality_var_id(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'vector_equality', (('VAR_ID','var1'),('VAR_ID','var2'))
		chain = func.get_if_chain([condition])
		
		self.assertEqual(chain, 'if score Global _var1_0 = Global _var2_0 if score Global _var1_1 = Global _var2_1 if score Global _var1_2 = Global _var2_2 ')
		
	def test_mcfunction_get_if_chain_vector_equality_sel_var_id(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'vector_equality', (('SEL_VAR_ID',('@sel1','var1')),('SEL_VAR_ID',('@sel2','var2')))
		chain = func.get_if_chain([condition])
		
		self.assertEqual(chain, 'if score @sel1 _var1_0 = @sel2 _var2_0 if score @sel1 _var1_1 = @sel2 _var2_1 if score @sel1 _var1_2 = @sel2 _var2_2 ')

	def test_mcfunction_mcfunction_get_if_chain_vector_equality_var_components(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'vector_equality', (('VAR_COMPONENTS',[('a1', 'x1'), ('b1', 'y1'), ('c1', 'z1')]),('VAR_COMPONENTS',[('a2', 'x2'), ('b2', 'y2'), ('c2', 'z2')]))
		chain = func.get_if_chain([condition])
		
		self.assertEqual(chain, 'if score a1 x1 = a2 x2 if score b1 y1 = b2 y2 if score c1 z1 = c2 z2 ')
		
	def test_mcfunction_mcfunction_get_if_chain_unless(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'vector_equality', (('VAR_ID','var1'),('VAR_ID','var2'))
		with self.assertRaises(ValueError):
			func.get_if_chain([condition], 'unless')
			
	def test_mcfunction_mcfunction_get_if_chain_block(self):
		env = mock_environment()
		env.block_tags['test_block_tag'] = ['test_block1']
		func = mcfunction.mcfunction(env)
		
		condition1 = 'block', (dummy_relcoords(1, 2, 3), 'test_block_tag')
		condition2 = 'block', (dummy_relcoords(4, 5, 6), 'test_block2')
		chain = func.get_if_chain([condition1, condition2])
		
		self.assertEqual(chain, 'if block 1 2 3 #test_namespace:test_block_tag if block 4 5 6 minecraft:test_block2 ')

	def test_mcfunction_mcfunction_get_if_chain_bad_type(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		condition = 'bad', None
		with self.assertRaises(ValueError):
			func.get_if_chain([condition])
			
	def test_mcfunction_execute_command_multiple_as(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		cmd = func.get_execute_command([('As', None), ('As', None)], exec_func)
		self.assertEqual(cmd, None)
		
	def test_mcfunction_execute_command_if(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'If', [('selector', '@p')]
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute if entity @p ')
		
	def test_mcfunction_execute_command_unless(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'Unless', [('selector', '@p')]
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute unless entity @p ')
		
	def test_mcfunction_execute_command_as_id_attype(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'AsId', (('Var', ('Global', 'test_var')), 'at_type')
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(func.commands, ['scoreboard players operation Global _id = Global test_var'])
		self.assertEqual(cmd, 'execute as @e if score @s _id = Global _id ')
		self.assertEqual(exec_func.self_selector, '@at_type')
		
	def test_mcfunction_execute_command_as_id(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'AsId', (('Var', ('Global', 'test_var')), None)
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(func.commands, ['scoreboard players operation Global _id = Global test_var'])
		self.assertEqual(cmd, 'execute as @e if score @s _id = Global _id ')
	
	def test_mcfunction_execute_command_as_create(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		sel = mock_selector_definition()
		sel.type = 'creeper'
		env.selectors['test_id'] = sel
		
		item = 'AsCreate', create_block(0, 'test_id', relcoords([relcoord('', const_number('1')), relcoord('', const_number('2')), relcoord('', const_number('3'))]))
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(func.commands, [
			'scoreboard players add @e _age 1',
			'summon creeper 1 2 3 ',
			'scoreboard players add @e _age 1'
		])
		self.assertEqual(cmd, 'execute as @e[_age==1] ')
		
	def test_mcfunction_execute_command_as_create_multiple(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'AsCreate', create_block(0, 'test_id', ['1', '2', '3'])
		item2 = 'If', [('selector', '@p')]
		
		cmd = func.get_execute_command([item, item2], exec_func)
		
		self.assertEqual(cmd, None)
		
	def test_mcfunction_execute_command_rotated_etc(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		for type, code, target, target_code, extra in [
			('As', 'as', '@p', '@p', ''),
			('Rotated', 'rotated as', '@p', '@p', ''),
			('FacingCoords', 'facing', dummy_relcoords(1, 2, 3), '1 2 3', ''),
			('FacingEntity', 'facing entity', '@p', '@p', ' feet'),
			('Align', 'align', 'xyz', 'xyz', ''),
			('In', 'in', 'the_end', 'the_end', ''),
		]:
			item = type, target
			
			cmd = func.get_execute_command([item], exec_func)
			self.assertEqual(cmd, 'execute {} {}{} '.format(code, target_code, extra))
			
	def test_mcfunction_execute_command_at_selector_coords(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'At', ('@test_selector', dummy_relcoords(1, 2, 3))
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute at @test_selector positioned 1 2 3 ')
		
	def test_mcfunction_execute_command_at_selector(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'At', ('@test_selector', None)
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute at @test_selector ')
		
	def test_mcfunction_execute_command_at_coords(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'At', (None, dummy_relcoords(1, 2, 3))
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute positioned 1 2 3 ')
		
	def test_mcfunction_execute_command_at_vector(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'AtVector', (None, vector_var_expr('test_vector'))
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute at @e[_age == 1] ')
		self.assertEqual(func.commands, [
			'scoreboard players add @e _age 1',
			'summon area_effect_cloud',
			'scoreboard players add @e _age 1',
			'execute store result entity @e[_age==1,limit=1] Pos[0] double 0.001 run scoreboard players get Global _test_vector_0',
			'execute store result entity @e[_age==1,limit=1] Pos[1] double 0.001 run scoreboard players get Global _test_vector_1',
			'execute store result entity @e[_age==1,limit=1] Pos[2] double 0.001 run scoreboard players get Global _test_vector_2'
		])
		self.assertEqual(exec_func.commands, ['/kill @e[_age == 1]'])
		
	def test_mcfunction_execute_command_at_vector_scale(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item = 'AtVector', (const_number(200), vector_var_expr('test_vector'))
		
		cmd = func.get_execute_command([item], exec_func)
		self.assertEqual(cmd, 'execute at @e[_age == 1] ')
		self.assertEqual(func.commands, [
			'scoreboard players add @e _age 1',
			'summon area_effect_cloud',
			'scoreboard players add @e _age 1',
			'execute store result entity @e[_age==1,limit=1] Pos[0] double 0.005 run scoreboard players get Global _test_vector_0',
			'execute store result entity @e[_age==1,limit=1] Pos[1] double 0.005 run scoreboard players get Global _test_vector_1',
			'execute store result entity @e[_age==1,limit=1] Pos[2] double 0.005 run scoreboard players get Global _test_vector_2'
		])
		self.assertEqual(exec_func.commands, ['/kill @e[_age == 1]'])
		
	def test_mcfunction_execute_command_at_vector_multiple(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		exec_func = mock_mcfunction()
		
		item1 = 'AtVector', (const_number(200), vector_var_expr('test_vector'))
		item2 = 'AtVector', (const_number(200), vector_var_expr('test_vector'))
		
		cmd = func.get_execute_command([item1, item2], exec_func)
		self.assertEqual(cmd, None)
		
	def test_mcfunction_switch_cases_four(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		case1 = 1, 2, [mock_block('command1')], 0, None
		case2 = 3, 3, [mock_block('command2')], 0, None
		case3 = 4, 5, [mock_block('command3')], 0, None
		case4 = 6, 10, [mock_block('command4')], 0, None
		
		self.assertTrue(func.switch_cases('switch_var', [case1, case2, case3, case4]))
		self.assertEqual(func.commands, [
			'execute if score Global switch_var matches 1..2 run command1',
			'execute if score Global switch_var matches 3..3 run command2',
			'execute if score Global switch_var matches 4..5 run command3',
			'execute if score Global switch_var matches 6..10 run command4'
		])
		
	def test_mcfunction_switch_cases_three(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		case1 = 1, 2, [mock_block('command1')], 0, None
		case2 = 3, 3, [mock_block('command2')], 0, 'test_python_var'
		case3 = 4, 5, [mock_block('command3')], 0, None
		
		self.assertTrue(func.switch_cases('switch_var', [case1, case2, case3]))
		self.assertEqual(func.commands, [
			'execute if score Global switch_var matches 1..2 run command1',
			'execute if score Global switch_var matches 3..3 run command2',
			'execute if score Global switch_var matches 4..5 run command3'
		])
		self.assertEqual(env.cloned_environments[1].dollarid['test_python_var'], 3)
		
	def test_mcfunction_switch_cases_multiline(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		case1 = 1, 2, [mock_block('command1')], 0, None
		case2 = 3, 3, [mock_block('command2'), mock_block('command5')], 0, None,
		case3 = 4, 5, [mock_block('command3'), mock_block('command4')], 0, None
		
		self.assertTrue(func.switch_cases('switch_var', [case1, case2, case3]))
		self.assertEqual(func.commands, [
			'execute if score Global switch_var matches 1..2 run command1',
			'execute if score Global switch_var matches 3..3 run function test_namespace:case3_001_ln0',
			'execute if score Global switch_var matches 4..5 run function test_namespace:case4-5_001_ln0'
		])
		self.assertEqual(env.functions['case3_001_ln0'].commands, ['command2', 'command5'])
		self.assertEqual(env.functions['case4-5_001_ln0'].commands, ['command3', 'command4'])
		
	def test_mcfunction_switch_cases_five(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		case1 = 1, 2, [mock_block('command1')], 0, None
		case2 = 3, 3, [mock_block('command2')], 0, None
		case3 = 4, 5, [mock_block('command3')], 0, None
		case4 = 6, 10, [mock_block('command4')], 0, None
		case5 = 11, 15, [mock_block('command5')], 0, None
		
		self.assertTrue(func.switch_cases('switch_var', [case1, case2, case3, case4, case5]))
		self.assertEqual(func.commands, [
			'execute if score Global switch_var matches 1..2 run command1',
			'execute if score Global switch_var matches 3..3 run command2',
			'execute if score Global switch_var matches 4..5 run command3',
			'execute if score Global switch_var matches 6..15 run function test_namespace:switch6-15_001_ln0',
		])
		self.assertEqual(env.functions['switch6-15_001_ln0'].commands, [
			'execute if score Global switch_var matches 6..10 run command4',
			'execute if score Global switch_var matches 11..15 run command5'
		])
		
	def test_mcfunction_switch_cases_error(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		case1 = 1, 2, [mock_block('command1')], 0, None
		case2 = 3, 3, [mock_block('command2')], 0, 'test_python_var'
		case3 = 4, 5, [mock_block('command3')], 0, None
		case4 = 6, 7, [mock_block('command4')], 0, None
		case5 = 8, 9, [mock_block(raiseException=True, line=1)], 0, None
		
		self.assertFalse(func.switch_cases('switch_var', [case1, case2, case3, case4, case5]))
		
	def test_mcfunction_add_operation(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		func.add_operation('@test_selector', 'var1', '+=', 'var2')
		self.assertEqual(env.applied, [
			'@test_selector',
			'scoreboard players operation @test_selector var1 += @test_selector var2'
		])
		self.assertEqual(func.commands, ['scoreboard players operation @test_selector var1 += @test_selector var2'])
		
	def test_mcfunction_insert_command_empty(self):
		env = mock_environment()
		func = mcfunction.mcfunction(env)
		
		func.insert_command('', 0)
		self.assertEqual(func.commands, [])
		
	def test_mcfunction_get_vector_path(self):
		env = mock_environment()
		sel = mock_selector_definition()
		sel.vector_paths['test_var'] = 'path.to.data', 'float', None
		sel.is_single_entity = True
		env.selectors['test_selector'] = sel
		env.selector_definitions['@test_selector[x=1]'] = sel
		func = mcfunction.mcfunction(env)
		
		self.assertTrue(func.get_vector_path('@test_selector[x=1]', 'test_var', ['assign_var1', 'assign_var2', 'assign_var3']))
		self.assertEqual(func.commands, [
			'execute store result score Global assign_var1 run data get entity @test_selector[x=1] path.to.data[0] 1000',
			'execute store result score Global assign_var2 run data get entity @test_selector[x=1] path.to.data[1] 1000',
			'execute store result score Global assign_var3 run data get entity @test_selector[x=1] path.to.data[2] 1000'
		])
		
	def test_mcfunction_set_selector_path(self):
		env = mock_environment()
		sel = mock_selector_definition()
		sel.vector_paths['test_var'] = 'path.to.data', 'float', None
		sel.is_single_entity = True
		env.selectors['test_selector'] = sel
		env.selector_definitions['@test_selector[x=1]'] = sel
		func = mcfunction.mcfunction(env)
		
		self.assertTrue(func.set_vector_path('@test_selector[x=1]', 'test_var', ['x', 'y', 'z']))
		self.assertEqual(func.commands, [
			'execute store result entity @test_selector[x=1] path.to.data[0] float 0.001 run scoreboard players get Global x',
			'execute store result entity @test_selector[x=1] path.to.data[1] float 0.001 run scoreboard players get Global y',
			'execute store result entity @test_selector[x=1] path.to.data[2] float 0.001 run scoreboard players get Global z'
		])
		
	def test_environment_clone(self):
		gc = mock_global_context()
		env = environment.environment(gc)
		
		new_env = env.clone('new_name')
		
		self.assertEqual(new_env.scratch.prefix, 'new_name_prefix')
		
	def test_environment_copy_dollarid(self):
		gc = mock_global_context()
		env = environment.environment(gc)
		
		env.dollarid['test1'] = '10'
		env.copy_dollarid('$test2', '-$test1')
		
		self.assertTrue('test2' in env.dollarid)
		self.assertEqual(env.dollarid['test2'], '-10')
		
		env.dollarid['test3'] = '20.0'
		env.copy_dollarid('$test4', '-$test3')

		self.assertTrue('test4' in env.dollarid)
		self.assertEqual(env.dollarid['test4'], '-20.0')

		env.dollarid['test5'] = 'string'
		with self.assertRaises(ValueError) as context:
			env.copy_dollarid('$test6', '-$test5')
	
		
if __name__ == '__main__':
    unittest.main()