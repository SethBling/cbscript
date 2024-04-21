# Python dependencies:
# * ply
# * pyyaml

import os
import sys
import time

from cb_script import cbscript, scriptparse, source_file

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
