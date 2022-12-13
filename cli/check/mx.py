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

from lib import check, commons
import dns.resolver
import time
import os.path

def http2mx(target: str) -> str:
    target = target.replace("https://", "")
    target = target.replace("http://", "")
    if target.startswith("www."):
        target = target[4:]
    return target
    
checksToRun = {}
def checkMX(automatism: check.Input, hosts):
    target = http2mx(automatism.address)
    poisonedHosts = []
    try:
        answers = dns.resolver.resolve(target, 'MX')
        for rdata in answers:
            exchange = rdata.exchange.to_text().lower()
            for marker in hosts:
                if marker in exchange:
                    poisonedHosts.append(str(rdata.preference) + " " + exchange)
    except KeyboardInterrupt:
        raise
    except:
        pass
    return poisonedHosts

def usage():
    print("""
./cli/check/mx.py out/$SOURCE/$DATE/dataset.tsv

Identifica i siti con record MX problematici

Where:
- $SOURCE is a folder dedicated to a particular data source
- $DATE is the data source creation date in ISO 8601 format (eg 2022-02-28)
""")
    sys.exit(-1)

def addHostCheck(dataset, checksToRun, hostsFile):
    """
    Registra in checksToRun la verifica Python relativa alla
    presenza degli host elenencati in hostFiles.
    """
    hostsFilePath = './cli/check/mx/%s' % hostsFile
    #commons.eprint("jsFilePath %s" % jsFilePath)
    if not (hostsFile.endswith('.hosts') and os.path.isfile(hostsFilePath)):
        return # nothing to do

    hosts = []
    with open(hostsFilePath, "r") as f:
        for line in f:
            line = line.strip(" \n\r")
            if line[0] == "#":
                continue
            if len(line) > 3:
                hosts.append(line)
    outputFile = check.outputFileName(dataset, 'mx', hostsFile.replace('.hosts', '.tsv'))
    directory = os.path.dirname(outputFile)
    #commons.eprint("mkdir %s", directory)
    os.makedirs(directory, 0o755, True)
    checksToRun[hostsFile] = {
        'hosts': hosts,
        'output': open(outputFile, "w", buffering=1, encoding="utf-8")
    }

def loadMXChecks(dataset):
    files = os.listdir('./cli/check/mx/')
    files = sorted(files)
    for file in files:
        #commons.eprint("loaded host", file)
        addHostCheck(dataset, checksToRun, file)

def main(argv):
    if len(argv) != 2:
        usage()

    dataset = argv[1]

    if not os.path.isfile(dataset):
        print("not found: " + dataset);
        usage()
    
    loadMXChecks(dataset)
    
    count = 0
    try:
        with open(dataset, 'r') as inf:
            for line in inf:
                automatism = check.parseInput(line)
                if automatism.type != 'Web':
                    continue

                for c in checksToRun:
                    try:
                        execution = check.Execution(automatism)
                        hosts = checksToRun[c]['hosts']
                        outf = checksToRun[c]['output']
                        issues = checkMX(automatism, hosts)
                        if len(issues) == 0:
                            execution.complete()
                        else:
                            execution.complete(str(issues))
                    except (KeyboardInterrupt):
                        raise
                    except Exception as e:
                        execution.interrupt(str(e))
                    outf.write(str(execution)+'\n')
                    commons.eprint(count, execution);

                time.sleep(1)
                count += 1
                
    except (KeyboardInterrupt):
        print("Interrupted at %s" % count)

if __name__ == "__main__":
    main(sys.argv)
