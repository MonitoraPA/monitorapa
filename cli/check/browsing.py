#!/usr/bin/env -S python3 -u

# This file is part of MonitoraPA
#
# Copyright (C) 2022-2023 Giacomo Tesio <giacomo@tesio.it>
# Copyright (C) 2022 Leonardo Canello <leonardocanello@protonmail.com>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)

import sys
sys.path.insert(0, '.') # NOTA: da eseguire dalla root del repository git
import signal
signal.signal(signal.SIGINT, signal.default_int_handler)

from lib import commons, check

import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException
from http.client import RemoteDisconnected

import time
import os
import os.path
import psutil
import shutil
import tempfile
import socket
import json
from urllib.parse import urlparse
from datetime import datetime

def usage():
    commons.eprint("""
./cli/check/browsing.py out/$SOURCE/$DATE/dataset.tsv

Where:
- $SOURCE is a folder dedicated to a particular data source
- $DATE is the data source creation date in ISO 8601 format (eg 2022-02-28)
""")
    sys.exit(-1)

checksToRun = {}
networkLogs = []

def run(dataset):
    """
    Esecuzione dell'osservatorio sul dataset fornito.
    
    - carica le verifiche in checkToRun dalle cartelle in cli/check/browsing/
    - crea una cartella per la cache in out/.../check/browsing/
    - crea un istanza del browser
    - apre il dataset e per ogni riga
      - esegue le verifiche in checkToRun
    - alla fine (o su un SIGINT o Ctrl+C)
      - chiude il browser
      - cancella la cartella della cache
    """
    loadAllChecks(dataset, checksToRun)
    cacheDir = getCacheDir(dataset)
    
    browser = openBrowser(cacheDir)

    count = 0
    try:
        with open(dataset, 'r') as inf:
            for line in inf:
                count += 1
                
                #if count < 266:
                #    continue

                automatism = check.parseInput(line)
                if automatism.type != 'Web':
                    continue


                commons.eprint()
                print(count, automatism);
                
                try:
                    runChecks(automatism, browser)
                except BrowserNeedRestartException:
                    if browserReallyNeedARestart(browser):
                        browser = restartBrowser(browser, cacheDir)
                    
                #if count % 500 == 499:
                #    browser = restartBrowser(browser, cacheDir)
                count += 1
    except (KeyboardInterrupt):
        commons.eprint("Interrupted at %s" % count)
    finally:
        browser.quit()
        time.sleep(5)
        shutil.rmtree(cacheDir, False)

## Python checks
GoogleFontsHostNames = [
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'themes.googleusercontent',
]
FontsExt = [
    '.ttf',
    '.woff',
    '.woff2'
]

def eventToEvidence(event):
    """
    Estrae l'evidenza di un trasferimento dall'evento
    """
    evidence = {}
    if event['method'] == 'Network.requestWillBeSent':
        evidence['url'] = event['params']['request']['url'] 
        #evidence['request'] = event['params']['request']

        #requestID = event['params']['requestId']
        #extraInfos = None
        #for log in networkLogs:
        #    if log['method'] == 'Network.requestWillBeSentExtraInfo' and event['params']['requestId'] == requestID:
        #        extraInfos = event['params']
        #        break
        #if extraInfos != None:
        #    evidence['cookies'] = extraInfos['associatedCookies']
        #    evidence['headers'] = extraInfos['headers']
        #else:
        #    evidence['cookies'] = []
        #    evidence['headers'] = evidence['request']['headers']
    else:
        raise ValueError(str(event))
    return evidence['url']

def checkConnectedHosts(browser, poisonedHosts):
    """
    Analizza le richieste registrate in network logs alla 
    ricerca di host compromessi
    """
    global networkLogs
    evidences = []
    for event in networkLogs:
        if event['method'] != 'Network.requestWillBeSent':
            continue
        #if event['params']['documentURL'] != browser.current_url:
        #    commons.eprint("Ignoring %s from %s" % (event['params']['request']['url'], event['params']['documentURL']))
        #    continue
        rawUrl = event['params']['request']['url']

        if rawUrl == 'https://monitora-pa.it/tools/ping.html':
            # vedi browseTo() e browserReallyNeedARestart()
            continue

        url = urlparse(rawUrl)

        host = url.netloc
        if ':' in host:
            host = host[0:host.index(':')]
        evidence = eventToEvidence(event)
        
        if host in poisonedHosts:
            evidences.append(evidence)
        else:
            for phost in poisonedHosts:
                if phost[0] == '.':
                    if host.endswith(phost):
                        evidences.append(evidence)
                        break
                    elif host == phost[1:] :
                        evidences.append(evidence)

                        break
    if len(evidences) == 0:
        return ""
    
    if len(evidences) > 1:
        evidences = list(set(evidences))
    return json.dumps(evidences)

def checkActualUrl(browser):
    """
    Semplice verifica che riporta semplicemente la url di
    atterraggio a valle dei vari redirect che possono avvenire
    all'accesso ad un sito web
    """
    return browser.current_url

def checkCookies(browser):
    """
    Verifica che estrae i cookie registrati nel browser.
    """
    res = browser.execute_cdp_cmd('Network.getAllCookies', {})
    cookies = res['cookies']
    if len(cookies) == 0:
        return ""
    return json.dumps(cookies)

def checkGoogleFonts(browser):
    """
    Verifica della presenza di trasferimenti verso Google Fonts.
    """
    global networkLogs
    evidences = []
    
    for event in networkLogs:
        if event['method'] != 'Network.requestWillBeSent':
            continue
        if event['params']['documentURL'] != browser.current_url:
            continue
        url = urlparse(event['params']['request']['url'])
        host = url.netloc
        if ':' in host:
            host = host[0:host.index(':')]
        if host in GoogleFontsHostNames:
            if '/css' in url.path:
                evidences.append(eventToEvidence(event))
            else:
                for ext in FontsExt:
                    if url.path.endswith(ext):
                        evidences.append(eventToEvidence(event))
                        break
    if len(evidences) == 0:
        return ""
    if len(evidences) > 1:
        evidences = list(set(evidences))
    return json.dumps(evidences)

def checkGoogleReCAPTCHA(browser):
    """
    Verifica della presenza di trasferimenti verso Google reCAPTCHA.
    """
    global networkLogs
    evidences = []
    for event in networkLogs:
        if event['method'] != 'Network.requestWillBeSent':
            continue
        if event['params']['documentURL'] != browser.current_url:
            continue
        url = urlparse(event['params']['request']['url'])
        host = url.netloc
        if ':' in host:
            host = host[0:host.index(':')]
        if host.endswith('recaptcha.net'):
            evidences.append(eventToEvidence(event))
        elif host == 'www.google.com' and url.path.startswith('/recaptcha/api.js'):
            evidences.append(eventToEvidence(event))
    if len(evidences) == 0:
        return ""
    if len(evidences) > 1:
        evidences = list(set(evidences))
    return json.dumps(evidences)

## Check execution

def runChecks(automatism, browser):
    """
    Esegue le verifiche in checksToRun per la url dell'automatismo.
    
    - naviga il browser verso la pagina richiesta
    - esegue le verifiche python che iniziano con "000-"
    - esegue le verifiche JavaScript
      - che possono causare navigazioni fra pagine e quindi
        ritornare risultati parziali (si veda jsFramework)
    - scrolla alla fine della pagina
    - esegue le altre verifiche python
    - esegue le verifiche python che iniziano con "999-"
    - in caso di eccezione registra l'errore per tutte le verifiche successive
      - se la rete è irraggiungibile, attende il ripristino
      - in caso di alcune eccezioni può sollevare BrowserNeedRestartException
        che causerà la sostituzione dell'istanza del browser
    """
    url = automatism.address

    results = {}
    jsChecksCount = countJSChecks(checksToRun)

    try:
        browseTo(browser, url)
        actual_url = browser.current_url

        runPythonChecks('000-', results, browser)
        
        #time.sleep(20)  # to wait for F12
        
        while countJSChecks(results) != jsChecksCount:
            if actual_url != browser.current_url:
                browseTo(browser, actual_url)

            waitUntilPageLoaded(browser)

            # due to the async nature of some check operations
            # we need to regenerate and run this script several times
            # collecting results provided by each run and excluding
            # the previous executed tests.
            script = jsFramework;        
            allChecks = ""
            for toRun in checksToRun:
                if toRun in results:
                    continue
                if checksToRun[toRun]['type'] == 'js':
                    checkCode = checksToRun[toRun]['script']
                    allChecks += singleJSCheck % (toRun, checkCode)

            script += runAllJSChecks % allChecks
            script += "return runAllJSChecks();";
        
            newResults = executeInBrowser(browser, script)

            #commons.eprint('script executed:', newResults)
            for js in newResults:
                if newResults[js]['issues'] != None:
                    results[js] = newResults[js]
        
        scrollToBottom(browser)
        
        time.sleep(2)
        executeInBrowser(browser, 'window.stop()')
        browser.get("about:black")
        time.sleep(3)
        
        for toRun in checksToRun:
            if toRun in results:
                continue
            if checksToRun[toRun]['type'] == 'py':
                runPythonCheck(checksToRun, toRun, results, browser)
 
        runPythonChecks('999-', results, browser)
        
        completionTime = str(datetime.now())
                
        for js in checksToRun:
            execution = check.Execution(automatism)
            issues = results[js]['issues']
            if results[js]['completed']:
                execution.complete(issues, completionTime)
            else:
                execution.interrupt(issues, completionTime)
            #commons.eprint("execution of %s:" % js, str(execution))
            checksToRun[js]['output'].write(str(execution)+'\n')
    except RemoteDisconnected as err:
        commons.eprint("RemoteDisconnected", err.msg)
        raise BrowserNeedRestartException
    except WebDriverException as err:
        commons.eprint("WebDriverException of type %s occurred" % err.__class__.__name__, err.msg)
        # un check ha causato una eccezione: 
        # - registro i risultati raccolti
        # - registro l'eccezione su tutti i check che non ho potuto eseguire
        failTime = str(datetime.now())
        for js in checksToRun:
            execution = check.Execution(automatism)
            if js in results:
                issues = results[js]['issues']
                if results[js]['completed']:
                    execution.complete(issues, failTime)
                else:
                    execution.interrupt(issues, failTime)
            else:
                issues = "%s: %s" % (err.__class__.__name__, err.msg)
                execution.interrupt(issues, failTime)
            checksToRun[js]['output'].write(str(execution)+'\n')

        if commons.isNetworkDown():
            commons.eprint('Network down: waiting...')
            commons.waitUntilNetworkIsBack()
            commons.eprint('Network restored: back to work')

        if err.__class__.__name__ == 'TimeoutException' and 'receiving message from renderer' in err.msg:
            raise BrowserNeedRestartException
        if 'invalid session id' in err.msg:
            raise BrowserNeedRestartException
        if 'chrome not reachable' in err.msg:
            raise BrowserNeedRestartException
    #time.sleep(100000)

def runPythonCheck(checks, toRun, results, browser):
    """
    Esegue la verifica toRun (se non già precedentemente eseguita)
    e salva i risultati in results
    """
    if toRun in results:
        return # nothing to do
    try:
        functionToRun = checksToRun[toRun]['function']
        checkResult = functionToRun(browser)
        #commons.eprint(f'{toRun} completed:', checkResult)
        results[toRun] = {
            'completed': True,
            'issues': checkResult
        }
    except Exception as err:
        commons.eprint(f'{toRun} interrupted:', str(err))
        raise
        results[toRun] = {
            'completed': False,
            'issues': str(err)
        }
    

def runPythonChecks(prefix, results, browser):
    """
    Esegue le verifica python in checksToRun che iniziano con il prefisso fornito
    e salva i risultati in results
    """
    for toRun in checksToRun:
        if not toRun.startswith(prefix):
            continue
        if checksToRun[toRun]['type'] != 'py':
            continue
        runPythonCheck(checksToRun, toRun, results, browser)

def loadAllChecks(dataset, checksToRun):
    """
    Carica in checksToRun le verifiche da effettuare:
    
    - quelle programmatiche, definite in questo script
      - checkActualUrl
      - checkCookies (all'inizio e alla fine)
      - checkGoogleFonts
      - checkGoogleReCAPTCHA
    - quelle JavaScript da ./cli/check/browsing/js/
    - quelle dipendenti dall'host contattato, da ./cli/check/browsing/js/
    
    NOTA BENE: l'ordine è rilevante: le verifiche JS vanno tenute al centro
    per permettere la registrazione di tutte le richieste analizzate successivamente
    via Python. 
    Di particolare rilevanza è ./cli/check/browsing/js/300-consent.js
    che accetta i tutti i cookie, permettendo il confronto fra prima e dopo
    l'accettazione.
    """
    addPythonCheck(dataset, checksToRun, '000-actual-url', checkActualUrl)
    addPythonCheck(dataset, checksToRun, '000-cookies', checkCookies)
    
    files = os.listdir('./cli/check/browsing/js/')
    files = sorted(files)
    for file in files:
        #commons.eprint("loaded js", file)
        addJSCheck(dataset, checksToRun, file)

    files = os.listdir('./cli/check/browsing/hosts/')
    files = sorted(files)
    for file in files:
        #commons.eprint("loaded host", file)
        addHostCheck(dataset, checksToRun, file)

    addPythonCheck(dataset, checksToRun, '999-cookies', checkCookies)
    addPythonCheck(dataset, checksToRun, '999-googlefonts', checkGoogleFonts)
    addPythonCheck(dataset, checksToRun, '999-googlerecaptcha', checkGoogleReCAPTCHA)

def addJSCheck(dataset, checksToRun, jsFile):
    """
    Registra in checksToRun la verifica JavaScript presente in jsFile
    """
    jsFilePath = './cli/check/browsing/js/%s' % jsFile
    #commons.eprint("jsFilePath %s" % jsFilePath)
    if not (jsFile.endswith('.js') and os.path.isfile(jsFilePath)):
        return # nothing to do

    js = ""
    with open(jsFilePath, "r") as f:
        js = f.read()
    outputFile = check.outputFileName(dataset, 'browsing', jsFile.replace('.js', '.tsv'))
    directory = os.path.dirname(outputFile)
    #commons.eprint("mkdir %s", directory)
    os.makedirs(directory, 0o755, True)
    checksToRun[jsFile] = {
        'type': 'js',
        'script': js,
        'output': open(outputFile, "w", buffering=1, encoding="utf-8")
    }

def hostsToPythonCheck(poisonedHosts):
    """
    Restituisce una funzione Python che prende il browser
    e analizza i log delle richieste registrate in networkLogs
    per identificare gli host problematici passati
    """
    def pythonCheck(browser):
        return checkConnectedHosts(browser, poisonedHosts)
    return pythonCheck
    
def addHostCheck(dataset, checksToRun, hostsFile):
    """
    Registra in checksToRun la verifica Python relativa alla
    presenza degli host elenencati in hostFiles.
    """
    hostsFilePath = './cli/check/browsing/hosts/%s' % hostsFile
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
    outputFile = check.outputFileName(dataset, 'browsing', hostsFile.replace('.hosts', '.tsv'))
    directory = os.path.dirname(outputFile)
    #commons.eprint("mkdir %s", directory)
    os.makedirs(directory, 0o755, True)
    checksToRun[hostsFile] = {
        'type': 'py',
        'function': hostsToPythonCheck(hosts),
        'output': open(outputFile, "w", buffering=1, encoding="utf-8")
    }

def countJSChecks(dictionary):
    """
    Restituisce il numero di verifiche JavaScript presenti nel dizionario
    """
    return len([c for c in dictionary if c.endswith('.js')])

def addPythonCheck(dataset, checksToRun, name, pythonFunction):
    """
    Registra in checksToRun una verifica python con il nome in `name`
    """
    outputFile = check.outputFileName(dataset, 'browsing', name + '.tsv')
    directory = os.path.dirname(outputFile)
    #commons.eprint("mkdir %s", directory)
    os.makedirs(directory, 0o755, True)
    checksToRun[name] = {
        'type': 'py',
        'function': pythonFunction,
        'output': open(outputFile, "w", buffering=1, encoding="utf-8")
    }

# Framework Javascript
jsFramework = """

if(!Object.hasOwn(window, 'MonitoraPA')){
    window.MonitoraPA = {};
    window.monitoraPACallbackPending = 0;
}

function monitoraPAWaitForCallback(){
    /* funzione da invocare prima di effettuare una 
     * operazione asincrona che determina l'invocazione
     * di una callback
     */
debugger;
    ++window.monitoraPACallbackPending;
}
function monitoraPACallbackCompleted(){
    /* funzione da invocare quando la callback è stata invocata
     * indipendentemente se con successo o con errore
     */
debugger;
    --window.monitoraPACallbackPending;
}

function monitoraPAClick(element){
    /* funzione da invocare per effettuare un click su un 
     * elemento HTML che può causare una navigazione 
     * (tipicamente button, a, input[type=submit] etc...)
     */
    monitoraPAWaitForCallback();
    window.setTimeout(function(){
        element.click();
    }, 2000);
    window.setTimeout(function(){
        // this will be executed only if no navigation occurred
        monitoraPACallbackCompleted();
    }, 6000);
}

window.monitoraPACache = {}
function monitoraPADownloadResource(uri){
    /* funzione da invocare per effettuare il download di una risorsa
     */
    if(Object.hasOwn(window.monitoraPACache, uri)){
        return window.monitoraPACache[uri];
    }
    window.monitoraPACache[uri] = '';
    var req = new XMLHttpRequest();
    req.open("GET", uri, false);
    req.onreadystatechange = function(){
        if (req.readyState === 4) {
            var content = req.responseText;
            window.monitoraPACache[uri] = content;
        }
    }
    req.send();
    return window.monitoraPACache[uri];
}


function runMonitoraPACheck(results, name, check){
    /* funzione invocata da browsing.py per eseguire
     * la verifica check, registrandone il valore di
     * ritorno in results
     */
    var issues;

    if(window.monitoraPAUnloading == true || window.monitoraPACallbackPending > 0){
        // skip check since a previous check caused a navigation
        return;
    }
    
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

# Template per l'esecuzione di una singola verifica: il contenuto
# dei file JS in ./cli/check/browsing/js/ diventa il corpo della
# funzione passata a runMonitoraPACheck
singleJSCheck = """
runMonitoraPACheck(monitoraPAResults, '%s', function(){
%s
});
"""

# Template per l'esecuzione delle verifiche Javascript
runAllJSChecks = """
function runAllJSChecks(){
debugger;
    var monitoraPAResults = {};
    window.monitoraPAResults = monitoraPAResults;

%s
    
    return window.monitoraPAResults;
}
"""


class BrowserNeedRestartException(Exception):
    """
    Eccezione sollevata quando è necessario riavviare il browser
    """
    pass

def executeInBrowser(browser, js):
    """
    Esegue il codice js nel browser e ritorna il risultato.
    In caso di alert che impedisca l'esecuzione, prova a chiuderlo e riprova.
    """
    #rprint('\n\nexecuting', js)
    try:
        return browser.execute_script(js)
    except UnexpectedAlertPresentException:
        try:
            time.sleep(3)
            alert = browser.switch_to.alert
            time.sleep(1)
            alert.accept()
        except NoAlertPresentException:
            pass
        return browser.execute_script(js)


## Browser control functions
def openBrowser(cacheDir):
    """
    Avvia il browser con cache in cacheDir.
    """
    op = uc.ChromeOptions()
    op.add_argument('--home='+cacheDir.replace('udd', 'home'))
    op.add_argument('--incognito')
    op.add_argument('--disable-popup-blocking')
    op.add_argument('--disable-extensions')
    op.add_argument('--dns-prefetch-disable')
    op.add_argument('--disable-gpu')
    op.add_argument('--disable-dev-shm-usage')
    op.add_argument('--ignore-ssl-errors')
    op.add_argument('--enable-features=NetworkServiceInProcess')
    op.add_argument('--disable-features=NetworkService,SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure')
    op.add_argument('--window-size=1920,1080')
    op.add_argument('--aggressive-cache-discard')
    op.add_argument('--disable-cache')
    op.add_argument('--disable-application-cache')
    op.add_argument('--disable-offline-load-stale-cache')
    op.add_argument('--disk-cache-size=' + str(5*1024*1024)) # 5MB
    op.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    chrome_path = os.path.join(os.getcwd(),'browserBin/chrome/chrome')
    driver_path = os.path.join(os.getcwd(),'browserBin/chromedriver/chromedriver')
    if os.name == 'nt': # Se viene eseguito su windows
        chrome_path += ".exe"
        driver_path += ".exe"
    headless=True
    browser = uc.Chrome(options=op, version_main=104, headless=headless, browser_executable_path=chrome_path, driver_executable_path=driver_path, enable_cdp_events=True)
    browser.get('about:blank')
    browser.add_cdp_listener('Network.requestWillBeSent', collectNetworkLogs)
    #browser.add_cdp_listener('Network.requestWillBeSentExtraInfo', collectNetworkLogs)
    #browser.add_cdp_listener('Network.responseReceived', collectNetworkLogs)
    #browser.add_cdp_listener('Network.responseReceivedExtraInfo', collectNetworkLogs)
    browser.set_page_load_timeout(90)
    return browser

def browseTo(browser, url):
    """
    Apre url in un nuovo tab del browser (eventualmente chiudendo i tab aperti su altri indirizzi)
    """
    # we are in incognito mode: each new tab get a clean state for cheap
    global networkLogs
    networkLogs = []
    
    while len(browser.window_handles) > 1:
        browser.switch_to.window(browser.window_handles[-1])
        browser.get('about:blank')
        browser.delete_all_cookies()
        browser.execute_cdp_cmd('Network.clearBrowserCache', {})
        browser.execute_cdp_cmd('Network.clearBrowserCookies', {})
        time.sleep(0.5)
        browser.close()
        
    browser.switch_to.window(browser.window_handles[0])
    browser.get('about:blank')
    browser.execute_cdp_cmd('Network.clearBrowserCache', {})
    browser.execute_cdp_cmd('Network.clearBrowserCookies', {})
    executeInBrowser(browser, "window.open('');")
    browser.switch_to.window(browser.window_handles[-1])
    
    browser.get('https://monitora-pa.it/tools/ping.html')
    while len(networkLogs) > 1:
        time.sleep(2)
        networkLogs = []
        browser.get('about:blank')
        browser.execute_cdp_cmd('Network.clearBrowserCache', {})
        browser.execute_cdp_cmd('Network.clearBrowserCookies', {})
        time.sleep(1)
        browser.get('https://monitora-pa.it/tools/ping.html')

    try:
        if len(networkLogs) > 1:
            print("Spurious Network logs: ", networkLogs)
        networkLogs = []
        browser.get(url)
        needRefresh = executeInBrowser(browser, 'return document.getElementsByTagName("body").length == 0;')
        if needRefresh:
            executeInBrowser(browser, 'window.location.reload();')
            time.sleep(2)
            browser.get('about:blank')
            browser.get(url)
    except TimeoutException:
        if len(browser.title) > 1:
            pass # after 90 something has been loaded anyway
        else:
            raise
    except WebDriverException as err:
        if url.startswith('http://') and ('net::ERR_CONNECTION_REFUSED' in err.msg or 'net::ERR_CONNECTION_TIMED_OUT' in err.msg):
            browseTo(browser, url.replace('http://', 'https://'))
            return
        else:
            raise
    executeInBrowser(browser, "window.addEventListener('unload', e => { window.monitoraPAUnloading = true; }, {capture:true});")
    #commons.eprint("browseTo DONE")

def waitUntilPageLoaded(browser, period=2):
    """
    Attende che la pagina sia caricata (fino ad un massimo di 60 volte il periodo)
    """
    #commons.eprint('waitUntilPageLoaded %s ' % browser.current_url, end='')
    
    readyState = False
    count = 0
    
    while not readyState and count < 60:
        time.sleep(period)
        readyState = executeInBrowser(browser, 'return document.readyState == "complete" && !window.monitoraPAUnloading && !window.monitoraPACallbackPending;')
        count += 1
    #commons.eprint()

def scrollToBottom(browser):
    script = """
function monitoraPAScrollDown(){
    var initialY = window.scrollY;
    if (typeof(initialY) !== 'number'){
        initialY = window.pageYOffset;
    }
    window.scrollBy({
      top: window.innerHeight/2,
      left: 0,
      behavior: 'smooth'
    });
    return initialY;
}
"""
    initialY = -1
    newY = 0
    loops = 0
    while newY > initialY and loops < 20:
        initialY = executeInBrowser(browser, script+" return monitoraPAScrollDown()")
        time.sleep(1)
        newY = executeInBrowser(browser, "return window.pageYOffset")
        loops += 1

def restartBrowser(browser, cacheDir):
    """
    Riavvia il browser
    """
    commons.eprint('restarting Browser: pid %d, dataDir %s' % (browser.service.process.pid, cacheDir))
    process = psutil.Process(browser.service.process.pid)
    tokill = process.children(recursive=True)
    tokill.append(process)
    browser.quit()
    time.sleep(10)
    for p in tokill:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass
    browser = None
    time.sleep(10)
    return openBrowser(cacheDir)

def collectNetworkLogs(event):
    """
    Registra i gli eventi di rete in networkLogs
    """
    networkLogs.append(event)
    #commons.eprint(event)

def browserReallyNeedARestart(browser):
    """
    Naviga una pagina nota per stabilire se il browser necessiti veramente di un riavvio.
    """
    try:
        browseTo(browser, 'https://monitora-pa.it/tools/ping.html')
    except:
        return True
    return False

def getCacheDir(dataset):
    """
    Determina la cartella della cache del browser
    """
    cacheDirsContainer = os.path.dirname(check.outputFileName(dataset, 'browsing', 'user-data-dirs', 'tmp.tsv'))
    os.makedirs(cacheDirsContainer, 0o755, True)
    cacheDir = tempfile.mkdtemp(prefix='udd-%d-' % os.getpid(), dir=cacheDirsContainer)
    return cacheDir

def main(argv):
    if len(argv) != 2:
        usage()

    dataset = argv[1]

    if not os.path.isfile(dataset):
        commons.eprint(f"input dataset not found: {dataset}");
        usage()
        
    run(dataset)


if __name__ == "__main__":
    main(sys.argv)
