#!/usr/bin/env python3

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)

import sys
sys.path.insert(0, '.') # NOTA: da eseguire dalla root del repository git
import os.path

from lib import commons

def usage():
    commons.eprint("""
./cli/data/università/normalize.py ./out/università/YYYY-MM-YY/enti.tsv

Will create ./out/università/YYYY-MM-YY/dataset.tsv
""")
    sys.exit(-1)

def outputFileName(inputFileName):
    return os.path.join(os.path.dirname(inputFileName), "dataset.tsv")

def normalizeUrl(url):
    url = url.strip().lower()
    if len(url) < 4 or url.startswith('about'):
        return ""
    if "@pec.it" in url or "@gmail.com" in url or "@istruzione.it" in url or "@libero.it" in url or "@yahoo.it" in url:
        return "" # skip mail addresses
    if url.startswith('about:'):
        return ""
    if url == "blank":
        return ""
    if url.find(':') == 4 and url[0:7] != 'http://':
        return url.replace(url[0:5], 'http://')
    if url.find(':') == 5 and url[0:8] != 'https://':
        return url.replace(url[0:6], 'https://')
    if url.startswith('https//'):
        return url.replace('https//', 'https://')
    if url.startswith('http//'):
        return url.replace('http//', 'http://')
    if not url.startswith('http'):
        return 'http://' + url
    return url
    
def main(argv):
    if len(argv) != 2:
        usage()
    try:
        outFileName = outputFileName(argv[1])
        with open(argv[1], "r") as inf, open(outFileName, "w") as outf:
            i = 0
            for line in inf:
                if i == 0:
                    i += 1 # skip column headers
                    continue
                line = line.strip(" \r\n")
                fields = line.split('\t')
                if fields[4].strip() != "Attivo":
                    continue
                outID = fields[1].strip()
                webSite = normalizeUrl(fields[12])
                if webSite != '':
                    outf.write('\t'.join([outID, 'Web', webSite]) + '\n')

        print(f"{outFileName}")           
    except IOError as ioe:
        commons.eprint(f"IOError: {ioe}")
        usage()

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit(1)
