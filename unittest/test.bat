@ECHO OFF
set PYTHONPATH=..
call coverage run --omit ./* unit_test.py 2> %tmp%\test_results.txt
call coverage report
call coverage html
type %tmp%\test_results.txt