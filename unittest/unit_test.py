import cbscript
import unittest
import mock_source_file
import mock_mcfunction
import mcfunction
import global_context
import block_types.command_block

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
		
	def test_compile_command(self):
		func = mock_mcfunction.mock_mcfunction()
		cbscript.compile(func, ('Command', 'say hi'))
		self.assertTrue('say hi' in func.add_command_log)
		
		func = mock_mcfunction.mock_mcfunction()
		block = block_types.command_block.command_block(0, 'say hi')
		block.compile(func)
		self.assertTrue('say hi' in func.add_command_log)
			
if __name__ == '__main__':
    unittest.main()