import cbscript
import unittest
import mock_source_file
import mcfunction
import global_context

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
		
	def test_get_friendly_name_and_random_variable(self):
		for filename, friendly_name in [
			('test.cbscript', 'test'),
			('TEST.cbscript', 'test'),
			('test', 'test'),
			('test test.cbscript', 'test_test'),
			('test:test.cbscript', 'test_test'),
			('test,test.cbscript', 'test_test'),
			('test{}test.cbscript', 'test__test'),
			('test=test.cbscript', 'test_test'),
			]:
			source = mock_source_file.mock_source_file(base_name = filename)
			script = cbscript.cbscript(source)
			self.assertEqual(script.get_friendly_name(), 'CB' + friendly_name)
			self.assertEqual(script.get_random_objective(), 'RV' + friendly_name)
		
			
if __name__ == '__main__':
    unittest.main()