# Python dependencies:
# * ply
# * pyyaml

import cbscript
import sys
import time

if len(sys.argv) <> 2:
	print "You must include a script filename."
	exit()

script = cbscript.cbscript(sys.argv[1])


def run():
	while True:
		script.check_for_update()
			
		time.sleep(1)
	
run()