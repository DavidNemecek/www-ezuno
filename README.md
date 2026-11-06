# ezuno – statische Website

20 HTML-Seiten mit eigenem CSS, JavaScript und einfachen Icons. Für den Betrieb
sind weder WordPress noch Plugins oder ein Formularserver nötig. Firmenbilder
bleiben erhalten; die fünf lokalen Schriftdateien stehen unter SIL OFL 1.1.
Herkunft und Grenzen stehen in [LICENSE-REVIEW.md](LICENSE-REVIEW.md).

Nur die **sieben ehemaligen Formularstellen** enthalten vorbereitete E-Mail-Buttons:
kostenlose Lizenz, Verkauf und Support. Alle gehen an `ezuno@ezuno.com`.
Andere Buttons führen zu den entsprechenden Abschnitten; gewöhnliche E-Mail-Links
bleiben einfache Kontaktlinks. Besucher ergänzen und versenden den Entwurf im
eigenen Mailprogramm. [EMAIL-TEMPLATES.md](EMAIL-TEMPLATES.md) zeigt die drei
aktuellen Texte; [FORM-MAPPING.md](FORM-MAPPING.md) dokumentiert die Originalfelder.

Die Website lädt keine Analysebibliothek und verwendet selbst keine Cookies
oder Browserspeicher. Vimeo wird erst beim bewussten Start des Videos geladen.

## Download und Pages

Der Download ist eine normale Datei unter
`releases/ezuno-5.10.19-Installation-Package.zip`, mit SHA-256-Prüfsumme daneben.
Sie ist **411.970.655 Bytes** groß und unverändert aus dem bereitgestellten
Installationspaket übernommen. Der Link benötigt weder JavaScript noch einen
GitHub-Account und funktioniert in einem Pages-Projektunterverzeichnis.

GitHub erlaubt keine einzelnen Git-Dateien über 100 MiB. Deshalb liegt das
Paket in `download-source/` in neun Teilen unter je 50 MiB. Der Pages-Build
prüft alle Hashes und erzeugt daraus **eine vollständige ZIP-Datei**.
Die Teile werden nicht als Website-Dateien veröffentlicht. Der Build benötigt
weder den privaten WordPress-Export noch einen Release oder Git LFS.

```powershell
python tools\package_download.py assemble
python tools\build_site.py
```

Der erste Befehl stellt den Download im lokalen Quellverzeichnis bereit;
der zweite erstellt die gesamte auslieferbare Website unter `_site/`.
Beide benötigen nur Python. Die fertigen ZIP-Dateien und `_site/` sind Git-ignoriert.

Der Workflow [pages.yml](.github/workflows/pages.yml) baut und veröffentlicht
bei Änderungen auf `main` sowie per manuellem Workflow-Start.
Als Pages-Quelle muss **GitHub Actions** eingerichtet sein. Nur der geprüfte
Website-Bestand einschließlich Download und Lizenzen wird hochgeladen.
Die gesamte Website bleibt mit etwa 415 MB unter dem 1-GB-Pages-Limit.
Quellen: [Git-Dateigrößen](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github),
[Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages),
[Pages-Limits und Nutzungsbedingungen](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

## Pflege und Prüfung

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe tools\modernize.py --prune
python tools\package_download.py assemble
.\.venv\Scripts\python.exe tools\check_links.py
.\.venv\Scripts\python.exe tools\verify_site.py
```

HTML-Inhalte werden direkt in den vorhandenen Seiten gepflegt. Empfänger und
Vorlagen stehen zentral in `tools/static_forms.py`; `modernize.py` überträgt
Änderungen auf alle Seiten. `tools/mirror.py --offline` ruft dieselbe Pflege auf
und lädt keine WordPress-Pakete mehr herunter.

Die Browserprüfung verwendet Edge oder einen Playwright-Browser. Ohne Edge:
`.\.venv\Scripts\python.exe -m playwright install chromium`.
Ein anderer Browserpfad kann über `EZUNO_BROWSER` gesetzt werden.
Ergebnisse und Prüfgrenzen stehen in [VERIFICATION.md](VERIFICATION.md).

## Export ohne Git-Historie

```powershell
python tools\export_site.py
```

`.mirror/rebuild/ezuno-static-clean.zip` enthält die aktuelle Website
einschließlich vollständigem Installer und Schriftlizenzen. Backups, Git-Historie,
Quellteile, Entwicklungswerkzeuge und Prüfcaches sind nicht enthalten.

