# Windows

## Comandi
### Requisiti
- [Python 3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Curl](https://curl.se/windows/)

NB: Curl, una volta scaricato, deve essere scompattato e copiato nella directory C:\. Inoltre va impostata la variabile di ambiente. Tutti i comandi elencati vanno eseguiti da CMD e non da PowerShell

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
```
```
Expand-Archive chrome.zip
```

Scarichiamo il binario di chromedriver e lo scompattiamo
```
curl.exe -L "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1012738%2Fchromedriver_win32.zip?generation=1654818846211970&alt=media" --output chromedriver.zip
```
```
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
```
```
python cli\data\enti\normalize.py out\enti\$data\enti.tsv
```
In questo punto se vuoi usare firefox come driver invece che chrome esegui il seguente comando
```
set SELECTED_BROWSER=firefox
```
Avviamo il check. Ricorda anche qua di sistemare la data.
```
$data=(Get-Date -Format "yyyy-MM-dd")
```
```
python cli\check\browsing.py out\enti\$data\dataset.tsv
```
