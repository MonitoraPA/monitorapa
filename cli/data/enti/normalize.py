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
    print("""
./cli/data/enti/normalize.py ./out/enti/YYYY-MM-YY/enti.tsv

Will create ./out/enti/YYYY-MM-YY/dataset.tsv
""")
    sys.exit(-1)

def outputFileName(inputFileName):
    return os.path.join(os.path.dirname(inputFileName), "dataset.tsv")

def normalizeUrl(url):
    url = url.lower()
    if len(url) < 4 or url.startswith('about'):
        return ""
    if url == "anagrafesquillace@libero.it":
        return "https://www.comune.squillace.cz.it/"
    if url == "enna@cert.ordine-opi.it":
        return "https://www.opienna.it/"
    if url == "rmic8bv005@istruzione.it":
        return "https://www.icparcodiveio.edu.it/"
    if url == "sistemabibliotecario@yahoo.it":
        return "http://www.sbti.it/"
    if url == "serra.segreteria@gmail.com":
        return "https://comune.serrasantabbondio.pu.it/"
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
                if fields[8] == "S": # Ente_in_liquidazione
                    continue
                outID = fields[1]
                webSite = normalizeUrl(fields[29])
                if webSite != '':
                    outf.write('\t'.join([outID, 'Web', webSite]) + '\n')
                outf.write('\t'.join([outID, 'Email', fields[19]]) + '\n')  

        print(f"{outFileName}")           
    except IOError as ioe:
        commons.eprint(f"IOError: {ioe}")
        usage()

if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        sys.exit(1)
