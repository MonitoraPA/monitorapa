# Comandi
Questa è una lista di comandi/istruzioni sul come preparare l'osservatorio per la sua funzione su debian e generalizzata il più possibile.
## Controlli preliminari
Prima di iniziare controlliamo che sia tutto aggiornato
```
sudo apt-get update
```
```
sudo apt-get upgrade
```
## Procedimento
Installiamo i comandi di GitHub
```
sudo apt-get install git
```
Cloniamo la repo
```
git clone https://github.com/MonitoraPA/monitorapa.git
```
Entriamo nella repo
```
cd monitorapa
```
Installiamo python3
```
sudo apt-get install python3
```
Aggiungiamo la possibilità di creare ambienti virtuali per python. Su altre distro potrebbe non essere necessario/chiamarsi diversamente:
```
sudo apt-get install python3-venv
```
Installiamo unzip per scompattare gli zip. Su altre distro potrebbe non essere necessario
```
sudo apt-get install unzip
```
Installiamo curl per scaricare successivamente i binari
```
sudo apt-get install curl
```
Creiamo l'ambiente virtuale e lo attiviamo
```
python3 -m venv .venv
```
Attiviamo l'ambiente virtuale (é consigliabile lavore in ambiene virtuale così che le modifiche non vengano apportate all'intero sistema ma solo all'ambiente)
```
source .venv/bin/activate
```
Installiamo le dipendenze richieste per eseguire gli script
```
pip install -r requirements.txt
```

Entriamo nella cartella dove posizioneremo i binari dei browser:
```
cd browserBin
```

Scarichiamo il binario di chrome e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012822%2Fchrome-linux.zip?generation=1654830630689916&alt=media' --output chrome.zip

unzip chrome.zip -d chrome && cp -R chrome/chrome-linux/* chrome && rm -rf chrome/chrome-linux
```
Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012822%2Fchromedriver_linux64.zip?generation=1654830636205228&alt=media' --output chromedriver.zip

unzip chromedriver.zip -d chromedriver && cp -R chromedriver/chromedriver_linux64/* chromedriver && rm -rf chromedriver/chromedriver_linux64
```
Installiamo le librerie necessarie (qualora non già presenti)
```
sudo apt-get install libdrm2 libgbm1 libasound2
```
Usciamo dalla cartella
```
cd ..
```
Eseguiamo il download del dataset
```
python3 cli/data/enti/download.py
```
Normalizziamo il dataset, ricorda di aggiustare il comando così da usare la data odierna!
```
python3 cli/data/enti/normalize.py out/enti/$(date "+%Y-%m-%d")/enti.tsv 
```
In questo punto se vuoi usare firefox come driver invece che chrome esegui il seguente comando
```
export SELECTED_BROWSER=firefox
```
Avviamo il check. Ricorda anche qua di sistemare la data.
```
python3 cli/check/browsing.py out/enti/$(date "+%Y-%m-%d")/dataset.tsv
```

# Comandi
Questa è una lista di comandi/istruzioni sul come preparare l'osservatorio per la sua funzione su FreeBSD e generalizzata il più possibile.
## Controlli preliminari
Prima di iniziare controlliamo che sia tutto aggiornato
```
sudo pkg update
```
```
sudo pkg upgrade
```
# Sei su FreeBSD e vuoi eseguire l'osservatorio?
Installiamo i comandi di GitHub
```
sudo pkg install git
```
Cloniamo la repo
```
git clone https://github.com/MonitoraPA/monitorapa.git
```
Entriamo nella repo
```
cd monitorapa
```
Installiamo sudo da root
```
pkg install sudo
```
Installiamo nano
```
pkg install nano
```
Adesso modifichiamo sudoers
```
nano /usr/local/etc/sudoers
```
scorrendo il file, alla voce root=ALL (ALL:ALL) ALL 
```
sotto questa riga scriviamo
```
utentet=ALL (ALL:ALL) ALL
```
da tastiera lanciare il comando CTRL+X e premere Y per confermare
```
Installiamo python3
```
sudo pkg install python39 py39-pip
```
Aggiungiamo la possibilità di creare ambienti virtuali per python. Su altre distro potrebbe non essere necessario/chiamarsi diversamente:
```
sudo pkg install py39-virtualenv
```
Installiamo unzip per scompattare gli zip. Su altre distro potrebbe non essere necessario
```
sudo pkg install unzip
```
Installiamo curl per scaricare successivamente i binari
```
sudo pkg install curl
```
Installiamo compact-linux per far funzionare chrome
```
sudo pkg install linux-c7
```
Per installare compact-linux si deve abilitare il modulo
```
sudo kldload linux64

```
Creiamo l'ambiente virtuale e lo attiviamo
```
virtualenv -p /usr/local/bin/python39 .venv --distribute
```
Attiviamo l'ambiente virtuale (é consigliabile lavore in ambiene virtuale così che le modifiche non vengano apportate all'intero sistema ma solo all'ambiente)
```
python .venv/bin/activate_this.py
```
Installiamo le dipendenze richieste per eseguire gli script
```
pip install -r requirements.txt
```

Entriamo nella cartella dove posizioneremo i binari dei browser:
```
cd browserBin
```

Scarichiamo il binario di chrome e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012822%2Fchrome-linux.zip?generation=1654830630689916&alt=media' --output chrome.zip

unzip chrome.zip -d chrome && cp -R chrome/chrome-linux/* chrome && rm -rf chrome/chrome-linux
```
Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012822%2Fchromedriver_linux64.zip?generation=1654830636205228&alt=media' --output chromedriver.zip

unzip chromedriver.zip -d chromedriver && cp -R chromedriver/chromedriver_linux64/* chromedriver && rm -rf chromedriver/chromedriver_linux64
```
Installiamo le librerie necessarie (qualora non già presenti)
```
sudo pkg install mesa-dri mesa-libs alsa-lib
```
Usciamo dalla cartella
```
cd ..
```
Eseguiamo il download del dataset
```
python3 cli/data/enti/download.py
```
Normalizziamo il dataset, ricorda di aggiustare il comando così da usare la data odierna!
```
python3 cli/data/enti/normalize.py out/enti/$(date "+%Y-%m-%d")/enti.tsv 
```
In questo punto se vuoi usare firefox come driver invece che chrome esegui il seguente comando
```
export SELECTED_BROWSER=firefox
```
Avviamo il check. Ricorda anche qua di sistemare la data.
```
python3 cli/check/browsing.py out/enti/$(date "+%Y-%m-%d")/dataset.tsv
```
# Sei su Windows e vuoi eseguire l'osservatorio?

Requisiti
- [Python 3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Curl](https://curl.se/windows/)

NB: Curl, una volta scaricato, deve essere scompattato e copiato nella directory C:\. Inoltre va impostata la variabile di ambiente. Tutti i comandi elencati vanno eseguiti da CMD e non da PowerShell

Cloniamo la repo
```
git clone https://github.com/MonitoraPA/monitorapa.git
```
Entriamo nella repo
```
cd monitorapa
```
Creiamo l'ambiente virtuale e lo attiviamo
```
python -m venv .venv
```
```
.\.venv\Scripts\activate.bat
```
Installiamo le dipendenze richieste per eseguire gli script
```
pip install -r requirements.txt
```

Entriamo nella cartella dove posizioneremo i binari dei browser:
```
cd browserBin
```

Scarichiamo il binario di chrome e lo scompattiamo
```
curl.exe -L "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1012738%2Fchrome-win.zip?generation=1654818664797684&alt=media" --output chrome.zip

Expand-Archive chrome.zip
```

Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl.exe -L "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1012738%2Fchromedriver_win32.zip?generation=1654818846211970&alt=media" --output chromedriver.zip

Expand-Archive chromedriver.zip
```
Usciamo dalla cartella
```
cd ..
```
Eseguiamo il download del dataset
```
python cli\data\enti\download.py
```
Normalizziamo il dataset, ricorda di aggiustare il comando così da usare la data odierna!
```
$data=(Get-Date -Format "yyyy-MM-dd")
python cli\data\enti\normalize.py out\enti\$data\enti.tsv
```
In questo punto se vuoi usare firefox come driver invece che chrome esegui il seguente comando
```
set SELECTED_BROWSER=firefox
```
Avviamo il check. Ricorda anche qua di sistemare la data.
```
$data=(Get-Date -Format "yyyy-MM-dd")
python cli\check\browsing.py out\enti\$data\dataset.tsv
```

# Procedimento per ottenere il binario di chrome/chromedriver

Partendo dalla prima risposta a questa domanda: https://superuser.com/questions/920523/where-can-i-download-old-stable-builds-of-chromium-from, traduco ed adatto

Guarda la versione che ti interessa (ad esempio "104.0.5112.0") nel [Position Lookup](https://omahaproxy.appspot.com/)

In questo caso ci ritorna la posizione "1012729". Questo è il commit a cui fa riferimento la versione di interesse.

Apri [l'archivio delle build continuative](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html)

Clicca sul tuo sistema operativo (Linux/Mac/Win)

Incolla "1012729" nel campo per il filtro in alto ed aspetta che i risultati vengano caricati.

Riceverai un risultato, nel nostro caso: https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux/101272/

- A volte può succedere che dovrai diminuire il numero di commit fino a che trovi una build esistente. Nel nostro caso ho dovuto rimuovere l'ultimo numero

# Devi controllare un sito in particolare?

In caso tu voglia controllare un singolo sito basterà seguire il manuale fino alla normalizzazione del dataset.

Una volta normalizzato il dataset recati nella cartella 
```
$data=(Get-Date -Format "yyyy-MM-dd")
out/enti/$data
```
tramite l'esplora file del tuo sistema operativo (la data sarà diversa).
Apri il file dataset.tsv con il tuo editor di preferenza.

Ora che hai il file aperto potrai modificarlo a tuo piacimento per mantenere solo i siti da te desiderati/aggiungerne di nuovi.

Mi raccomando, presta attenzione alla formattazione!

Una volta modificato il file a tuo piacere, salvalo e riprendi a seguire le istruzioni del manuale per eseguire l'osservatorio sul nuovo dataset da te modificato!

# Vuoi usare Docker? Puoi!

ATTENZIONE: questa modalità d'esecuzione dell'osservatorio è sperimentale ed è supportata solo sui sistemi Linux

Cloniamo la repo
```
git clone https://github.com/MonitoraPA/monitorapa.git
```
Entriamo nella repo
```
cd monitorapa
```
Entriamo nella cartella
```
cd docker
```
Eseguiamo lo script di setup
```
bash docker.sh
```
Nello script vi chiederà di scegliere tra 1 e 2. Scrivete 1 e premete invio.

Dopo un po' vi ritroverete nel terminale del container docker con tutto preparato.

Qui potrete usare l'osservatorio come se foste in un qualunque altro sistema Linux. Se volete seguire il manuale iniziate dal download del dataset.

NB: Il container Docker al momento NON supporta l'utilizzo di Firefox come driver.
