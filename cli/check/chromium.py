#!/usr/bin/env python3

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
# Copyright (C) 2022 Leonardo Canello <leonardocanello@protonmail.com>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)

import sys

from lib import check

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from datetime import datetime
import os.path
import os

jsChecks = {}

jsFramework = """

function runMonitoraPACheck(results, name, check){
    var issues;
    try {
        issues = check();
        results[name] = {
            'completed': true,
            'issues': issues
        }
    } catch(e) {
        issues = "runMonitoraPACheck: " + e.name + ": " + e.message;
        results[name] = {
            'completed': false,
            'issues': issues
        }
    }
}
"""

singleJSCheck = """
runMonitoraPACheck(monitoraPAResults, '%s', function(){
%s
});
"""

runAllJSChecks = """
function runAllJSChecks(){
    var monitoraPAResults = {};
    window.monitoraPAResults = monitoraPAResults;

%s
    
    return window.monitoraPAResults;
}
"""

def usage():
    print("""
./cli/selenium.py out/$SOURCE/$DATE/dataset.tsv

Where:
- $SOURCE is a folder dedicated to a particular data source
- $DATE is the data source creation date in ISO 8601 format (eg 2022-02-28)
""")
    sys.exit(-1)


def waitUntilPageLoaded(browser, period=2):
    
    readyState = False
    
    while not readyState:
        time.sleep(period)
        readyState = browser.execute_script('return document.readyState == "complete" && !window.monitoraPAUnloading;')

def clickConsentButton(url, browser):
	# thanks Mauro Gorrino
    buttonsFound = 0
    xpaths = [
        "//button[contains(translate(., 'ACET', 'acet'), 'accett')]",
        "//a[contains(translate(., 'ACET', 'acet'), 'accett')]",
        "//button[contains(translate(., 'ACONST', 'aconst'), 'acconsent')]",
        "//a[contains(translate(., 'ACONST', 'aconst'), 'acconsent')]",
        "//button[text()[.='Ok' or .='OK' or .='ok']]",
        "//a[text()[.='Ok' or .='OK' or .='ok']]",
        "//button[contains(translate(., 'APROV', 'aprov'), 'approv')]",
        "//a[contains(translate(., 'APROV', 'aprov'), 'approv')]",
        "//button[contains(translate(., 'CAPITO', 'capito'), 'capito')]",
        "//a[contains(translate(., 'CAPITO', 'capito'), 'capito')]",
        "//button[contains(translate(., 'ALE', 'ale'), 'alle')]",
        "//a[contains(translate(., 'ALE', 'ale'), 'alle')]",
        "//button[contains(translate(., 'ACEPT', 'acept'), 'accept')]",
        "//a[contains(translate(., 'ACEPT', 'acept'), 'accept')]"
    ]
    listeningOnUnload = False
    for consentPath in xpaths:
        buttons = browser.find_elements("xpath", consentPath)
        for button in buttons:
            try:
                if not listeningOnUnload:
                    browser.execute_script("window.addEventListener('unload', e => { window.monitoraPAUnloading = true; });")
                    listeningOnUnload = True
                browser.execute_script("arguments[0].click()", button)
                buttonsFound += 1
                isUnloading = browser.execute_script("return window.monitoraPAUnloading == true;")
                if isUnloading:
                    waitUntilPageLoaded(browser)
                    return True
            except Exception:
                pass
    return buttonsFound > 0


def openBrowser():
    op = webdriver.ChromeOptions()
    op.add_argument('--headless')
    op.add_argument('--incognito')
    op.add_argument('--disable-web-security')
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-extensions')
    op.add_argument('--dns-prefetch-disable')
    op.add_argument('--disable-gpu')
    op.add_argument('--ignore-certificate-errors')
    op.add_argument('--ignore-ssl-errors')
    op.add_argument('enable-features=NetworkServiceInProcess')
    op.add_argument('disable-features=NetworkService')
    op.add_argument('--window-size=1920,1080')
    op.add_argument('--aggressive-cache-discard')
    op.add_argument('--disable-cache')
    op.add_argument('--disable-application-cache')
    op.add_argument('--disable-offline-load-stale-cache')
    op.add_argument('--disk-cache-size=0')

    browser = webdriver.Chrome('chromedriver', options=op)
    
    browser.get('about:blank')
    
    return browser
    
def browseTo(browser, url):
    # we are in incognito mode: each new tab get a clean state for cheap
    
    while len(browser.window_handles) > 1:
        browser.switch_to.window(browser.window_handles[-1])
        browser.close()
    browser.switch_to.window(browser.window_handles[0])
    browser.get('about:blank')
    # browser.delete_all_cookies()
    browser.execute_script("window.open('');")
    browser.switch_to.window(browser.window_handles[-1])
    browser.get(url)

def getPageContent(browser):
    dom = browser.page_source
    return dom
    
def runChecks(automatism, browser):
    url = automatism.address

    try:
        browseTo(browser, url)
        waitUntilPageLoaded(browser)
        
        consented = clickConsentButton(url, browser)
        if consented:
            time.sleep(2)
            waitUntilPageLoaded(browser)

        script = jsFramework;
        
        allChecks = ""
        for js in jsChecks:
            checkCode = jsChecks[js]['script']
            allChecks += singleJSCheck % (js, checkCode)

        script += runAllJSChecks % allChecks
        script += "return runAllJSChecks();";
        #print(script)
        
        results = browser.execute_script(script)
        
        #print("got results", results)
        
        for js in jsChecks:
            execution = check.Execution(automatism)
            if results[js]['completed']:
                execution.complete(results[js]['issues'].replace('\n', ' ').replace('\t', ' '))
            else:
                execution.interrupt(results[js]['issues'].replace('\n', ' ').replace('\t', ' '))
            print("execution in %s:" % js, str(execution))
            jsChecks[js]['output'].write(str(execution)+'\n')

    except WebDriverException as err:
        for js in jsChecks:
            execution = check.Execution(automatism)
            issues = "WebDriverException: %s" % err
            execution.interrupt(issues.replace('\n', ' ').replace('\t', ' '))
            jsChecks[js]['output'].write(str(execution)+'\n')

    #time.sleep(100000)

def loadChecks(dataset, checksToRun):
    files = os.listdir('./cli/check/selenium/')
    for jsFile in files:
        jsFilePath = './cli/check/selenium/%s' % jsFile
        #print("jsFilePath %s" % jsFilePath)
        if os.path.isfile(jsFilePath) and jsFile.endswith('.js'):
            js = ""
            with open(jsFilePath, "r") as f:
                js = f.read()
            outputFile = check.outputFileName(dataset, 'selenium', jsFile.replace('.js', '.tsv'))
            directory = os.path.dirname(outputFile)
            #print("mkdir %s", directory)
            os.makedirs(directory, 0o755, True)
            checksToRun[jsFile] = {
                'script': js,
                'output': open(outputFile, "w", buffering=1)
            }


def main(argv):
    if len(sys.argv) != 2:
        usage()

    dataset = sys.argv[1]

    if not os.path.isfile(dataset):
        print(f"input dataset not found {dataset}");
        usage()

    loadChecks(dataset, jsChecks)
    browser = openBrowser()

    count = 0
    try:
        with open(dataset, 'r') as inf:
            for line in inf:
                automatism = check.parseInput(line)
                if automatism.type != 'Web':
                    continue

                runChecks(automatism, browser)
                count += 1
    except (KeyboardInterrupt):
        print("Interrupted at %s" % count)

    browser.quit()


if __name__ == "__main__":
    main(sys.argv)
