# Python dependencies:
# * ply
# * pyyaml

import cbscript
import sys
import time
import source_file
import scriptparse
import os

if len(sys.argv) != 2:
	print("You must include a script filename.")
	exit()

source = source_file.source_file(sys.argv[1])

os.chdir(source.get_directory())

script = cbscript.cbscript(source, scriptparse.parse)
script.try_to_compile()


def run():
	while True:
		script.check_for_update()
			
		time.sleep(1)
	
run()
