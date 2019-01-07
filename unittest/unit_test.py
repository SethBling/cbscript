import cbscript
import unittest

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
			
if __name__ == '__main__':
    unittest.main()