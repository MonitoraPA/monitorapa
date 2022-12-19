# FreeBSD

## Comandi
Questa è una lista di comandi/istruzioni sul come preparare l'osservatorio per la sua funzione su FreeBSD e generalizzata il più possibile.
### Controlli preliminari
Prima di iniziare controlliamo che sia tutto aggiornato
```
sudo pkg update
```
```
sudo pkg upgrade
```
### Procedimento
Installiamo i comandi per usare Git (ed interfacciarci con Github)
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

sotto questa riga scriviamo
```
utentet=ALL (ALL:ALL) ALL
```
da tastiera lanciare il comando CTRL+X e premere Y per confermare

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