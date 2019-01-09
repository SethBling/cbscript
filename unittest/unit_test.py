import cbscript
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
		self.assertTrue(cbscript.isNumber(1))
		self.assertTrue(cbscript.isNumber(0))
		self.assertTrue(cbscript.isNumber(1.0))
		self.assertFalse(cbscript.isNumber(float('inf')))
		self.assertFalse(cbscript.isNumber(float('nan')))
		self.assertFalse(cbscript.isNumber(None))
		self.assertFalse(cbscript.isNumber('test'))
		
	def test_factor(self):
		self.assertEqual(list(cbscript.factor(20)), [2, 2, 5])
		self.assertEqual(list(cbscript.factor(2)), [2])
		self.assertEqual(list(cbscript.factor(1)), [])
		
	def test_compile_runs_without_error(self):
		func = mock_mcfunction()
	
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
		
		block = execute_block(0, [], [('Command', 'test_command')])
		block.compile(func)
		
		block = for_index_block(0, 'test', ('NUM', 0), ('NUM', 5), ('NUM', 2), [('Command', 'test_command')])
		block.compile(func)
		
		block = for_selector_block(0, '@test', '@a', [('Command', 'test_command')])
		block.compile(func)
		
		block = function_call_block(0, 'test_function', [])
		block.compile(func)
		
		func.macros['test_macro'] = ([], [('Command', 'test_command')])
		block = macro_call_block(0, 'test_macro', [])
		block.compile(func)
		
		block = method_call_block(0, '@test_selector', 'test_method', [])
		block.compile(func)
		
		block = move_block(0, '@a', ['0', '0', '0'])
		block.compile(func)
		
		block = python_assignment_block(0, 'test_id', '1+1')
		block.compile(func)
		
		block = python_for_block(0, 'test_id', 'range(3)', [('Command', 'test_command')])
		block.compile(func)
		
		block = python_if_block(0, 'True', [('Command', 'true_command')], [('Command', 'false_command')])
		block.compile(func)
		block = python_if_block(0, 'False', [('Command', 'true_command')], [('Command', 'false_command')])
		block.compile(func)
		
		var = ('Var', ('@s', 'test'))
		block = scoreboard_assignment_block(0, var, '+=', ('NUM', 1))
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
		case1 = ('python', ('test_id', 'range(3, 6)', [('Command', 'test_python')]))
		case2 = ('range', ('1', '2', [('Command', 'test_range_1_2')]))
		block = switch_block(0, ('NUM', 1), [case1, case2])
		block.compile(func)
		
		block = tell_block(0, '@a', '{rhi')
		block.compile(func)
		
		func.template_functions['test_template_function'] = ([], [], [('Command', 'test_command')])
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
		
		block = while_block(0, [], [('Command', 'test_command')])
		block.compile(func)
		
	def test_compile_comment(self):
		func = mock_mcfunction()

		cbscript.compile(func, ('Comment', '#test'))
		self.assertTrue('#test' in func.add_command_log)
			
	def test_compile_command(self):
		func = mock_mcfunction()

		cbscript.compile(func, ('Command', 'say hi'))
		self.assertTrue('say hi' in func.add_command_log)
		
	def test_compile_move(self):
		func = mock_mcfunction()

		cbscript.compile(func, ('Move', ('@s', ('1', '1', '1'))))
		self.assertTrue('execute at @s run tp @s 1 1 1' in func.add_command_log)

		cbscript.compile(func, ('Move', ('@a', ('^0', '^0', '^1'))))
		self.assertTrue('execute as @a at @s run tp @s ^0 ^0 ^1' in func.add_command_log)
		
	def test_compile_python_assignment(self):
		func = mock_mcfunction()
		
		ret = cbscript.compile(func, ('PythonAssignment', ('test', '1+1')))
		self.assertTrue(ret)
		self.assertTrue('test' in func.dollarid)
		self.assertEqual(func.dollarid['test'], 2)
		
		ret = cbscript.compile(func, ('PythonAssignment', ('test2', '1/0')))
		self.assertFalse(ret)
		self.assertEqual(len(func.dollarid), 1)

		ret = cbscript.compile(func, ('PythonAssignment', ('test3', 'math.sqrt(9)')))
		self.assertTrue(ret)
		self.assertTrue('test3' in func.dollarid)
		self.assertEqual(func.dollarid['test3'], 3)
		
	def test_compile_python_for(self):
		func = mock_mcfunction()
		
		ret = cbscript.compile(func, ('For', ('i', 'range(3)', [('Command', '/say $i')])))
		self.assertTrue(ret)
		self.assertEqual(len(func.add_command_log), 3)
		
		ret = cbscript.compile(func, ('For', ('i', '[]', [])))
		self.assertTrue(ret)
		
		ret = cbscript.compile(func, ('For', ('i', '1', [])))
		self.assertFalse(ret)
	
		ret = cbscript.compile(func, ('For', ('i', 'range(1/0)', [])))
		self.assertFalse(ret)
	
	def test_compile_selector_assignment(self):
		func = mock_mcfunction()
		
		cbscript.compile(func, ('SelectorAssignment', ('test', '@s[x=1]')))
		
		self.assertEqual(func.atid['test'], '@s[x=1]')
		
if __name__ == '__main__':
    unittest.main()