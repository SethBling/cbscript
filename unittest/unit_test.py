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
		
if __name__ == '__main__':
    unittest.main()