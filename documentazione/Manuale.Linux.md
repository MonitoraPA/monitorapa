# Linux

## Comandi
Questa è una lista di comandi/istruzioni sul come preparare l'osservatorio per la sua funzione su debian e generalizzata il più possibile.
### Controlli preliminari
Prima di iniziare controlliamo che sia tutto aggiornato
```
sudo apt-get update
```
```
sudo apt-get upgrade
```
### Procedimento
Installiamo i comandi per usare Git (ed interfacciarci con Github)
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
```
```
unzip chrome.zip -d chrome && cp -R chrome/chrome-linux/* chrome && rm -rf chrome/chrome-linux
```
Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl -L 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012822%2Fchromedriver_linux64.zip?generation=1654830636205228&alt=media' --output chromedriver.zip
```
```
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