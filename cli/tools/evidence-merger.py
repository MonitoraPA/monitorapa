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
names['999-googlerecaptcha'] = "reCAPTCHA (Google LLC)"
names['999-googlefonts'] = "Google Fonts (Google LLC)"
names['500-adobe'] = "Adobe Inc."
names['501-aws'] = "Amazon Web Services, Inc."
names['502-moatads'] = "Moat Ads"
names['503-azure'] = "Microsoft Azure (Microsoft Corporation)"
names['504-facebook'] = "Facebook (Meta Platforms, Inc.)"
names['505-fontawesome'] = "FontAwesome (Cloudflare, Inc.)"
names['506-googlemaps'] = "Google Maps (Google LLC)"
names['507-cloudfront'] = "CloudFront (Amazon, Inc)"
names['508-microsoft'] = "Microsoft Corporation"
names['509-googlehostedlibraries'] = "Google Hosted Libraries (Google LLC)"
names['510-twitter'] = "Twitter, Inc."
names['511-youtube'] = "YouTube (Google LLC)"
names['512-googletagmanager'] = "Google Tag Manager (Google LLC)"
names['513-googleanalytics'] = "Google Analytics (Google LLC)"
names['514-unpkg'] = "Unpkg (Cloudflare, Inc.)"
names['515-akamai'] = "Akamai CDN (Akamai Technologies, Inc.)"
names['516-cloudflareinsights'] = "CloudflareInsights (Cloudflare, Inc.)"
names['517-jsdelivr'] = "JsDelivr (Cloudflare, Inc.)"
names['518-hcaptcha'] = "hCaptcha (Intuition Machines, Inc.)"
names['519-turnstile'] = "Turnstile (Cloudflare, Inc.)"
names['520-cdnjs'] = "cdnjs (Cloudflare, Inc.)"
names['521-jquery'] = "jquery.com (StackPath)"
names['522-vimeo'] = "Vimeo (Vimeo, Inc.)"
names['523-fastly'] = "Fastly"
names['524-addthis'] = "AddThis (Oracle Corporation)"
names['525-addtoany'] = "AddToAny"
names['526-googletranslate'] = "Google Translate (Google LLC)"
names['527-yandex'] = "Yandex LLC"
names['528-tencent'] = "Tencent Holdings Ltd."
names['529-alibaba.hosts'] = "Alibaba Group Holding Limited"
names['530-cloudflarecdn.hosts'] = "Cloudflare CDN (Cloudflare, Inc.)"
names['531-googlesearch'] = "Google Search (Google LLC)"
names['532-googledoubleclick'] = "Google Advertising (Google LLC)"


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
