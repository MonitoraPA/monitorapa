#!/usr/bin/env python3

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
# Copyright (C) 2022 Leonardo Canello <leonardocanello@protonmail.com>
# Copyright (C) 2022 Andrea Foletto <andrea@yaaaw.it>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)

import sys
import requests
import datetime
import os
import shutil

def verifyExecutionDirectory():
    if not os.path.isdir("cli") or not os.path.isfile("LICENSE.txt"):
        sys.exit(1)

    if not os.path.isdir("out"):
        os.mkdir("out")

    if not os.access("out", os.W_OK):
        sys.exit(1)


def computeOutDir():

    verifyExecutionDirectory()

    dirName = f"out/enti/{datetime.datetime.utcnow().strftime('%Y-%m-%d')}"

    if not os.path.isdir(dirName):
        os.makedirs(dirName, 0o755, True)

    if not os.path.isfile(os.path.join(dirName, "LICENSE.txt")):
        shutil.copy(
            os.path.abspath("LICENSE.txt"),
            os.path.abspath(dirName)
        )

    if not os.path.isfile(os.path.join(dirName, "README.md")):
        with open(os.path.join(dirName, "README.md"), "w") as readmeFile:
            readmeFile.write(
                f"""
This folder has been created by Monitora PA on {os.path.basename(dirName)}.
https://monitora-pa.it/

The file enti.tsv has been created by AgID and distributed under CC BY 4.0.
An up-to-date version can be downloaded from https://indicepa.gov.it/ipa-dati/dataset/enti

Everything else inside this folder can be used according to the terms 
and conditions of the Hacking License.

Read LICENCE.txt for the exact terms and conditions applied.
"""
            )

    return dirName

def main():
    outDir = computeOutDir()
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    url = 'https://indicepa.gov.it/ipa-dati/datastore/dump/d09adf99-dc10-4349-8c53-27b1e5aa97b6?bom=True&format=tsv'
    response = requests.get(url, allow_redirects=True, headers=headers)

    with open(f"{outDir}/enti.tsv", "wb") as outFile:
        outFile.write(response.content)

    print(f"{outDir}/enti.tsv")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
