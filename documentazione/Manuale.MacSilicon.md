# Mac - Silicon

## Comandi
Questa è una lista di comandi/istruzioni sul come preparare l'osservatorio per la sua funzione su dispositivi Apple con MacOS con CPU Apple Silicon e generalizzata il più possibile.
### Controlli preliminari
Prima di iniziare controlliamo se è installato XCode Command Tools

Il pacchetto XCode Command Tools contiene tutti gli eseguibili che servono per poter usare l'osservatorio

Aprire il terminale e lanciare il comando
```
xcode-select --install
```
Una volta installato riavviare il sistema e installare brew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Infine controllare che sia tutto aggiornato
```
brew update && brew upgrade
```
### Procedimento
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
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac_Arm%2F1084799%2Fchrome-mac.zip?generation=1671396509003354&alt=media' --output chrome.zip
```
```
unzip chrome.zip -d chrome && cp -R chrome/chrome-mac/* chrome && rm -rf chrome/chrome-mac
```
Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Mac_Arm%2F1084799%2Fchromedriver_mac64.zip?generation=1671396514328396&alt=media' --output chromedriver.zip
```
```
unzip chromedriver.zip -d chromedriver && cp -R chromedriver/chromedriver_mac64/* chromedriver && rm -rf chromedriver/chromedriver_mac64
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
export SELECTED_BROWSER=/Applications/Firefox/Contents/MacOS/firefox
```
Avviamo il check. Ricorda anche qua di sistemare la data.
```
python3 cli/check/browsing.py out/enti/$(date "+%Y-%m-%d")/dataset.tsv
```