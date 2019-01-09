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
		block = array_assignment_block(0, 'test', 'Const', 1, ('NUM', 1))
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
		
		block = for_index_block(0, 'test', ('NUM', 0), ('NUM', 5), ('NUM', 2), [command_block(0, 'test_command')])
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
		block = scoreboard_assignment_block(0, (var, '+=', ('NUM', 1)))
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
		block = switch_block(0, ('NUM', 1), [case1, case2])
		block.compile(func)
		
		block = tell_block(0, '@a', '{rhi')
		block.compile(func)
		
		func.template_functions['test_template_function'] = ([], [], [command_block(0, 'test_command')])
		block = template_function_call_block(0, 'test_template_function', [], [])
		block.compile(func)
		
		block = title_block(0, 'subtitle', '@a', ['1', '2', '3'], '{rtest')
		block.compile(func)
		
		var = ('VAR_ID', 'test')
		block = vector_assignment_block(0, var, '+=', ('VECTOR_HERE', 1000))
		block.compile(func)
		
		var = ('VAR_ID', 'test')
		block = vector_assignment_scalar_block(0, var, '+=', ('NUM', 1))
		block.compile(func)
		
		block = while_block(0, [], [command_block(0, 'test_command')])
		block.compile(func)
		
	def test_compile_comment(self):
		func = mock_mcfunction()
		block = comment_block(0, '#test')
		block.compile(func)
		self.assertTrue('#test' in func.add_command_log)
			
	def test_compile_command(self):
		func = mock_mcfunction()
		block = command_block(0, 'say hi')
		block.compile(func)
		self.assertTrue('say hi' in func.add_command_log)
		
	def test_compile_move(self):
		func = mock_mcfunction()
		block = move_block(0, '@s', ('1', '1', '1'))
		block.compile(func)
		self.assertTrue('execute at @s run tp @s 1 1 1' in func.add_command_log)

		block = move_block(0, '@a', ('^0', '^0', '^1'))
		block.compile(func)
		self.assertTrue('execute as @a at @s run tp @s ^0 ^0 ^1' in func.add_command_log)
		
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
		
if __name__ == '__main__':
    unittest.main()