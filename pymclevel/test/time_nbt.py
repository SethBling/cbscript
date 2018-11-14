from StringIO import StringIO

__author__ = 'Rio'

import pymclevel.nbt as nbt

from timeit import timeit

path = "testfiles/TileTicks.nbt"
test_data = file(path, "rb").read()

def load_file():
    global test_file
    test_file = nbt.load(buf=test_data)

def save_file():
    global resaved_test_file
    s = StringIO()
    resaved_test_file = test_file.save(compressed=False)
    #resaved_test_file = test_file.save(buf=s)
    #resaved_test_file = s.getvalue()

print "File: ", path
print "Load: %0.1f ms" % (timeit(load_file, number=1)*1000)
print "Save: %0.1f ms" % (timeit(save_file, number=1)*1000)
print "Length: ", len(resaved_test_file)

assert test_data == resaved_test_file
__author__ = 'Rio'
