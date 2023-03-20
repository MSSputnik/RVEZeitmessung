Zeit Modul für die RVE Langstrecke
==================================

Ziel
----

Ziel dieser Anwendung ist es, für die 3 Messpunkte (Start, 3000m und Ziel) eine möglichkeit zu bieten, die Absolute Zeit zu erfassen wann ein Boot die Marke passiert. Die Auswertung der gefahrenen Zeit erfolgt außerhalb dieses Systems.

Konfiguration
-------------

Die Konfiguration wird über die Datei 'RVEZeit.ini' erledigt. 

Parameter:

```ini
[DEFAULT]
# Positionen: Start, 3000m, Ziel
Position = Start

[FTP]
# FTP Server connection parameter
Server = fritz.box
User = ftpuser
Password = GeheimesKennwort123!
Directory = /Dokumente

```

Aufruf
------

Die Anwendung wurde unter Python 3.10.3 auf Windows entwickelt und getestet. 
Sie benötigt keine weiteren Module.

Start:

Windows:

```bat
cd RVEZeitmessung
py main.py

```

Linux:

```bash
cd RVEZeitmessung
python3 main.py

```
