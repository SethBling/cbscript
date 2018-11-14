rm _nbt.pyd
py.test test/nbt_test.py
python setup.py build_ext --inplace
py.test test/nbt_test.py

