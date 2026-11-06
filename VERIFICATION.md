# Prüfung des statischen Umbaus

Geprüft am **6. November 2026** mit Microsoft Edge/Chromium und Playwright.
Drei Subagents übernahmen Formularrekonstruktion, Darstellung, Browserprüfung
und unabhängige Inhalts-/Linkkontrolle.

## Ergebnis

**181/181 Prüfungen bestanden.** Bericht:
`.mirror/rebuild/review-runtime.json` (lokaler, nicht veröffentlichter Prüfcache).

- 120 Seitenfälle: alle 20 HTML-Seiten bei 1440 und 390 Pixeln, jeweils über
  HTTP, ein Pages-Projektunterverzeichnis und `file://`.
- 40 Fälle ohne JavaScript: alle Seiten bei beiden Breiten; Navigation und
  Inhalte bleiben erreichbar.
- 6 Interaktionsfälle: Feature-Tabs einschließlich Tastatur, Testimonials,
  FAQ, Navigation, Video-Dialog, Fokus und Links zwischen Seiten.
- 2 Downloadfälle: sofortiger nativer Download, Mehrfachklicksperre und
  Wiederfreigabe nach 15 echten Sekunden bei Desktop- und Mobilbreite.
- 3 zusätzliche Gesamtprüfungen: Formularvorlagen, lokale Verweise und
  vollständiger Installer mit relativer URL, SHA-256 und HTTP-HEAD.
- 10 Screenshots: Startbereich, Support, Kontakt, kostenlose Lizenz und
  Download bei beiden Breiten; Desktop-Startseite und mobiler Download
  zusätzlich visuell kontrolliert.

Keine JavaScript-Fehler, lokalen HTTP-Fehler, anfänglichen externen Anfragen
oder horizontale Überbreite. 426 Bildinstanzen wurden erfolgreich dekodiert,
einschließlich versteckter und verzögert geladener Bilder. Keine kopierten
404-Seiten oder leeren Platzhalterlinks.

## Nur frühere Formulare erhalten Vorlagen

Genau **7 Stellen** enthalten vorbereitete E-Mail-Buttons:

| Seite | Zweck |
| --- | --- |
| `index.html` | kostenlose Lizenz und Verkauf |
| `home/index.html` | kostenlose Lizenz und Verkauf |
| `home/subscribe/index.html` | kostenlose Lizenz |
| `home/contact/index.html` | Verkauf |
| `support/index.html` | Support |

Die drei Entwürfe gehen an `ezuno@ezuno.com`. Andere Aktionsbuttons führen zu
diesen Abschnitten. Die 8 gewöhnlichen E-Mail-Links verwenden dieselbe Adresse
ohne Entwurf. Die Prüfung erzwingt diese Trennung, sinnvolle zweckbezogene Texte,
vollständige URL-Kodierung und CRLF-Zeilenumbrüche. Alte CF7-Platzhalter fehlen.

Es werden keine Nachrichten versendet. Zustellbarkeit des Postfachs und das
lokale Mailprogramm des Besuchers werden damit nicht geprüft.
Vorlagen: [EMAIL-TEMPLATES.md](EMAIL-TEMPLATES.md);
Originalfelder: [FORM-MAPPING.md](FORM-MAPPING.md).

## Dateien und Links

### Rückmeldung und Klicksperre beim Download

Der erste Klick löst den nativen Download sofort aus. Für 15 Sekunden zeigt
der Button „Der Download wird gleich gestartet“ und blockiert weitere
Aktivierungen; danach werden Beschriftung und Bedienbarkeit wiederhergestellt.
Der Timer beginnt beim ersten Klick und bleibt unabhängig von der tatsächlichen
Übertragungsdauer. Die übrigen Links, einschließlich Prüfsummen-Download,
erhalten keine Sperre.

Zwei Browserfälle (Desktop/HTTP und Mobil/Projektunterverzeichnis) bestätigen
jeweils: erster Download nach 0,011 beziehungsweise 0,014 Sekunden, elf weitere
Aktivierungen blockiert, Freigabe nach 15,022 beziehungsweise 15,019 Sekunden
und ein erfolgreicher zweiter Download. Die Tests verwenden eine kleine ZIP
am lokalen HTTP-Testserver; das echte Installationspaket wird dabei nicht
übertragen. Die Darstellung des gesperrten Buttons wurde bei beiden Breiten
visuell kontrolliert. Ohne JavaScript bleibt der ursprüngliche Download-Link
verwendbar.

Gezielt wiederholbar mit
`.\.venv\Scripts\python.exe tools\verify_site.py --download-only`;
Nachweis: `.mirror/rebuild/review-download-guard.json`.

### Ressourcen

`tools/check_links.py` bestätigt **410 lokale Verweise und 167 Ankerlinks**
in 20 HTML-Seiten; alle Ziele existieren. Keine PHP-Dateien vorhanden.
Nur `assets/site.css` und `assets/site.js` werden als CSS/JavaScript geladen;
insgesamt 42 referenzierte Assets. JavaScript-Syntax, Python-Kompilierung,
`git diff --check` und Idempotenz der Offline-Normalisierung bestehen.

Die unabhängige externe Kontrolle hat defekte Support-, Installer-, Signa-
und alte Alfresco-Dokumentationslinks gefunden und ersetzt. Kundenwebsites,
FAW-Impressum, neue Hyland-Dokumentation, Vimeo, X und Apple wurden erreichbar
bestätigt. Facebook führt zur Anmeldung. Microsoft war aus der Testumgebung
nicht zuverlässig automatisch prüfbar; es bleibt der offizielle HTTPS-Link.
Externe Erreichbarkeit kann sich später ändern.

Veraltete Formular-, Analytics-, Cookie- und Zahlungsportal-Aussagen wurden
in den technischen Abschnitten der Datenschutzerklärung angepasst. Die
Inhaltskontrolle ist keine vollständige juristische Datenschutzprüfung.

## Installer und Veröffentlichungsbestand

Das unveränderte Originalpaket hat **411.970.655 Bytes**, SHA-256:

```text
f0be70bc5429b551ad54cec24c579d4a3a8b9c865b81b0cbf7bb767877e672c3
```

Alle neun Quellteile und die zusammengesetzte Datei sind hashgeprüft;
alle 22 enthaltenen ZIP-Einträge bestehen die CRC-Prüfung. Fehlerhafte oder
fehlende Teile werden abgewiesen. Der Download und seine Dateigröße sind über
HTTP-HEAD am normalen Pfad und im Projektunterverzeichnis bestätigt.

`python tools/build_site.py` erstellt `_site/` mit **71 Dateien**, rund 415 MB.
Alle veröffentlichten HTML-/Asset-Dateien wurden mit den gepflegten Quellen
verglichen. Der Export `.mirror/rebuild/ezuno-static-clean.zip` besteht ebenfalls
die CRC-Prüfung und enthält den vollständigen Installer, keine SQL-/PHP-Dateien,
Backups, Git-Daten, Quellteile oder Entwicklungswerkzeuge.

Der direkte Pages-Download wurde nach erfolgreichem
[Deployment](https://github.com/fawhgb/www-ezuno/actions/runs/42246879284)
auch live bestätigt: HTTP-HEAD liefert 200 und exakt 411.970.655 Bytes;
ein Teilabruf liefert 206 und den korrekten ZIP-Dateianfang. Die Prüfsumme
ist ebenfalls öffentlich erreichbar. **69/69 veröffentlichte Ressourcen**,
darunter alle 20 HTML-Seiten, stimmen mit dem geprüften Build überein
(Text-Zeilenumbrüche normalisiert). Der nicht öffentlich ausgelieferte
`.nojekyll`-Deploymentmarker ist kein Website-Linkziel und ausgenommen.
Nachweise: `.mirror/rebuild/live-download-check.json` und `live-site-check.json`.

**Offen ist HTTPS der eigenen Domain:** GitHub meldet für `www.ezuno.com`
den Zertifikatsstatus `new`; HTTPS scheitert derzeit am Hostnamen des
Zertifikats. Die erfolgreichen Live-Checks oben verwenden deshalb ausdrücklich
HTTP. DNS zeigt auf GitHub Pages. Der verfügbare GitHub-Zugang hat Schreibrechte,
aber keine Rechte zum Ändern der Pages-/HTTPS-Einstellungen.
Der Betreiber hat die Pages-Quelle auf `GitHub Actions` umgestellt;
die API bestätigt `build_type: workflow`. Der eigene Workflow veröffentlicht
die geprüfte Website einschließlich zusammengesetztem Download.

## Video und Prüfgrenzen

Die Browsermatrix prüft den eigenen Video-Dialog mit einer kontrollierten
Testseite. Vimeo wird erst bei Wiedergabe eingebunden; beim Schließen wird
der Player entfernt und der Fokus zurückgegeben. Die externe Wiedergabe
hängt zusätzlich von Vimeo und der Verbindung des Besuchers ab.

Die älteren `verification-*-sha256.json`-Dateien dokumentieren frühere Stände.
Aktuelle Asset-Hashes stehen in `snapshot.json`.
Dateilizenzen, Git-Historie und Hostingbedingungen:
[LICENSE-REVIEW.md](LICENSE-REVIEW.md).

## Wiederholen

```powershell
python tools\package_download.py assemble
.\.venv\Scripts\python.exe tools\check_links.py
.\.venv\Scripts\python.exe tools\verify_site.py
node --check assets\site.js
python tools\export_site.py
```

## Nachprüfung der Website-Lizenzen

Die explizite GPL-Zuordnung der bearbeiteten Templatestruktur und die
Ausnahme für gesonderte Lizenzen in beiden Nutzungsbedingungen wurden ergänzt.
Der vollständige Browserlauf nach dieser Änderung besteht weiterhin
**181/181 Prüfungen**, einschließlich aller 20 Seiten auf Desktop und Mobil,
der Fälle ohne JavaScript und der Interaktionen. Der lokale Linklauf prüft
jetzt 412 Ressourcenverweise und 167 Anker erfolgreich.

`python tools/check_licenses.py` prüft alle 20 HTML-Lizenzhinweise, beide
Ausnahmen in den Nutzungsbedingungen, die lokalen Verweise zur Lizenzübersicht,
die drei unveränderten Lizenztexte und die fünf unveränderten Schriftdateien.
Der Build ruft diese Prüfung am zusammengestellten Veröffentlichungsbestand
auf. Der gebaute Bestand umfasst 71 Dateien und 414.584.031 Bytes einschließlich
des unveränderten Installers.

Zusätzlich wurde an temporären Kopien bestätigt, dass fehlender GPL-Text,
eine entfernte Ausnahme in den Nutzungsbedingungen und eine veränderte
Schriftdatei die Lizenzprüfung jeweils fehlschlagen lassen. Ein erneuter
Pflegelauf verändert die bereits korrigierten HTML-Dateien nicht.

Der Prüfer verwendet nur die Python-Standardbibliothek und läuft deshalb auch
im bestehenden GitHub-Pages-Workflow ohne zusätzliche Build-Abhängigkeiten.
Der eigenständige Aufruf für einen fertigen Build lautet:

```powershell
python tools\check_licenses.py --site _site
```
