#!/usr/bin/env -S python3 -u

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)


import sys
sys.path.insert(0, '.') # NOTA: da eseguire dalla root del repository git
import signal
signal.signal(signal.SIGINT, signal.default_int_handler)

from lib import commons, check

import os

def main(argv):
    if len(argv) != 2:
        usage()
    with os.scandir(argv[1]) as it:
        for entry in it:
            if not entry.is_file():
                print(entry.name)
    


def usage():
    commons.eprint("""
./cli/report/collect-data.py out/$SOURCE/

Where:
- $SOURCE is a folder dedicated to a particular data source
""")
    sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv)
