import argparse
from sys import argv
from os import chdir
from pathlib import Path
import time

import cbscript
from config import Config
import source_file
import scriptparse

program = argparse.ArgumentParser(
    "cbscript",
    "cbscript [options] file"
)
program.add_argument("--instance","-i",type=Path,default=None)
program.add_argument("--optimize","-o",type=int,default=None)
program.add_argument("--watch","-w", action="store_true")
program.add_argument("file",type=Path)

def main(*args):
    options = program.parse_args(args)
    Config.load()
    if options.instance:
        Config.instance_path = options.instance
    if options.optimize:
        Config.optm_level = options.optimize
    source = source_file.source_file(options.file)
    chdir(options.file.parent)
    script = cbscript.cbscript(source,scriptparse.parse)
    if options.watch:
        try:
            print("Press CTRL-C to stop")
            while True:
                script.check_for_update()
    
                time.sleep(1)
        except KeyboardInterrupt:
            print("Goodbye!")
    else:
        script.try_to_compile()

if __name__ == "__main__":
    main(*argv[1:])
