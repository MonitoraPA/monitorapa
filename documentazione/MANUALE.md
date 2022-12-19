# Manuale

Il progetto predispone vari manuali dedicati a vari sistemi, eccone una lista:

| Sistema     | File                                             |
|:------------|:-------------------------------------------------|
| Docker      | [Manuale.Docker.md](./Manuale.Docker.md)         |
| FreeBSD     | [Manuale.FreeBSD.md](./Manuale.FreeBSD.md)       |
| Linux       | [Manuale.Linux.md](./Manuale.Linux.md)           |
| MacIntel    | [Manuale.MacIntel.md](./Manuale.MacIntel.md)     |
| MacSilicon  | [Manuale.MacSilicon.md](./Manuale.MacSilicon.md) |
| Windows     | [Manuale.Windows.md](./Manuale.Windows.md)       |

## Procedimento per ottenere il binario di chrome/chromedriver

Partendo dalla prima risposta a questa domanda: https://superuser.com/questions/920523/where-can-i-download-old-stable-builds-of-chromium-from, traduco ed adatto

Guarda la versione che ti interessa (ad esempio "104.0.5112.0") nel [Position Lookup](https://omahaproxy.appspot.com/)

In questo caso ci ritorna la posizione "1012729". Questo è il commit a cui fa riferimento la versione di interesse.

Apri [l'archivio delle build continuative](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html)

Clicca sul tuo sistema operativo (Linux/Mac/Win)

Incolla "1012729" nel campo per il filtro in alto ed aspetta che i risultati vengano caricati.

Riceverai un risultato, nel nostro caso: https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux/101272/

- A volte può succedere che dovrai diminuire il numero di commit fino a che trovi una build esistente. Nel nostro caso ho dovuto rimuovere l'ultimo numero

## Devi controllare un sito in particolare?

In caso tu voglia controllare un singolo sito basterà seguire il manuale fino alla normalizzazione del dataset.

Una volta normalizzato il dataset recati nella cartella (dove yyyy-MM-dd solitamente è la data più recente)
```
out/enti/yyyy-MM-dd
```
tramite l'esplora file del tuo sistema operativo (la data sarà diversa).
Apri il file dataset.tsv con il tuo editor di preferenza.

Ora che hai il file aperto potrai modificarlo a tuo piacimento per mantenere solo i siti da te desiderati/aggiungerne di nuovi.

Mi raccomando, presta attenzione alla formattazione!

Una volta modificato il file a tuo piacere, salvalo e riprendi a seguire le istruzioni del manuale per eseguire l'osservatorio sul nuovo dataset da te modificato!