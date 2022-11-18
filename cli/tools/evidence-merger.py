#!/usr/bin/env -S python3 -u

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)


import sys
sys.path.insert(0, '.') # NOTA: da eseguire dalla root del repository git

from lib import commons, check
import json
import os
import os.path

def printUsage():
    print("""
./cli/tools/evidence-merger.py output/folder/ check1.tsv [check2.tsv [...]]

Merge the evidence collected for each transfer in a single file for each owner
in output/folder/ and print to standard output created file in the usual 
check.Execution TSV format.

Each file is named as the Owner's code followed by the .txt extension
and it contains something like:

```
check1
- evidence 1
- evidence 2
- evidence 3
check2
- evidence 1
- evidence 2
```

... and so forth.
""")

    sys.exit(-1)

names = {}
names['999-cookies'] = "Cookies After Consent"
names['999-aws'] = "Amazon Web Services, Inc."
names['999-adobe'] = "Adobe Inc."
names['999-azure'] = "Microsoft Azure (Microsoft Corporation)"
names['999-facebook'] = "Facebook (Meta Platforms, Inc.)"
names['999-fontawesome'] = "FontAwesome (Cloudflare, Inc.)"
names['999-googlefonts'] = "Google Fonts (Google LLC)"
names['999-googlemaps'] = "Google Maps (Google LLC)"
names['999-googlerecaptcha'] = "reCAPTCHA (Google LLC)"
names['999-microsoft'] = "Microsoft Corporation"
names['999-googlehostedlibraries'] = "Google Hosted Libraries (Google LLC)"
names['999-twitter'] = "Twitter, Inc."
names['999-youtube'] = "YouTube (Google LLC)"

def run(outputFolder, checks):
    aggregatedExecutions = {}
    for check in checks:
        checkName = checkNameFromFileName(check)
        with open(check, "r") as results:
            appendResultsToFiles(outputFolder, checkName, results, aggregatedExecutions)
    for owner in aggregatedExecutions:
        print(aggregatedExecutions[owner])

def appendResultsToFiles(outputFolder, checkName, results, aggregatedExecutions):
    for line in results:
        execution = check.parseExecution(line)
        if execution.completed == "1" and execution.issues != "":
            issues = list(set(json.loads(execution.issues)))
            owner = execution.owner
            outputFile = outputFolder + '/' + owner + '.txt'
            with open(outputFile, "a") as output:
                output.write(getNiceName(checkName) + '\n')
                for issue in issues:
                    try:
                        output.write('- ' + issue + '\n')
                    except:
                        print(issue)
                        raise
            if owner not in aggregatedExecutions:
                execution.type = 'CheckResultAggregation'
                execution.complete(outputFile, execution.time)
                aggregatedExecutions[owner] = execution

def checkNameFromFileName(fileName):
    fileName = os.path.basename(fileName)
    fileName = fileName.replace('.tsv', '')
    return fileName

def getNiceName(checkName):
    if checkName in names:
        return names[checkName]
    for name in names:
        if checkName.startswith(name):
            return names[name]
    raise ValueError("unknown check name: "+checkName)

def main(argv):
    if len(sys.argv) < 3:
        printUsage()

    outputFolder = argv[1]
    if not os.path.isdir(outputFolder):
        print("output folder is not an existing directory: " + outputFolder)
        printUsage()
        
    checks = []
    for i in range(2, len(argv)):
        if not os.path.isfile(argv[i]):
            print("%s is not an existing file." % argv[i])
            printUsage()
        checks.append(argv[i])

    run(outputFolder, checks)


if __name__ == "__main__":
    main(sys.argv)
