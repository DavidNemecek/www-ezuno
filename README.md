# ezuno.com – statische Kopie

Momentaufnahme von **https://ezuno.com/** vom **30. Oktober 2026**.
Die fertige Website besteht ausschließlich aus HTML, CSS, JavaScript, Bildern
und lokal gespeicherten Schriften. Kein WordPress, PHP, Datenbank, Paketmanager
oder Build-Schritt ist zum Öffnen oder Veröffentlichen erforderlich.

## Lokal öffnen

**`index.html` im Browser öffnen.** Alle internen Links funktionieren auch direkt
über `file://`. Die Cookie-Einstellungen werden dabei im lokalen Browserspeicher
gesichert, weil `file://` keine HTTP-Cookies unterstützt.

Optional kann ein beliebiger statischer Dateiserver verwendet werden, zum Beispiel:

```sh
python3 -m http.server 4173
```

Danach http://localhost:4173 öffnen. Python dient hier nur als optionaler
Dateiserver und wird von der Website selbst nicht benötigt.

## Enthaltene Seiten

Insgesamt **20 HTML-Seiten**, darunter alle 16 Inhaltsseiten aus der öffentlichen
Sitemap des Originals, die Startseite und die benötigten Alias-/Fehlerseiten:

- Startseite mit Navigation, vier Feature-Tabs, Video-Dialog, Preisen,
  Testimonials, Kundenkarussell und Cookie-Einstellungen
- Download mit Installationshinweisen und aufklappbaren Abschnitten
- Support mit FAQ und aufklappbaren Antworten
- Terms of Use, Privacy Policy und End-User License Agreement
- Die zusätzlich direkt aufrufbaren Seiten unter `/home/`, einschließlich
  About, Features, Video, Pricing, Clients und Contact
- Die Fehlerseiten, auf die der Blog-Link und ein alter Terms-of-Use-Link
  bereits im Original führen

Texte, Bilder, Layout, responsive Darstellung und die benötigten Frontend-Skripte
stammen aus dem Original. Die ursprünglich von PHP erzeugte Farbdatei liegt als
normale CSS-Datei vor. Die WordPress-Schnittstellen und das auf diesen Seiten
ungenutzte Google-Maps-Skript werden nicht geladen. Interne Links und Ressourcen
sind relativ und funktionieren auch unter einem GitHub-Pages-Unterverzeichnis.

## Verhalten des Originals

Die ursprünglich defekten `[contact-form-7 …]`-Platzhalter wurden am
31. Oktober 2026 durch statische Formulare für die kostenlose Lizenz,
Kontakt/Angebote und Support ersetzt. Sie prüfen Pflichtfelder und E-Mail-Adresse
und öffnen einen vorausgefüllten Entwurf an **ezuno@ezuno.com** im Mailprogramm.
Die Anfrage wird erst dort durch den Besucher versendet. Falls kein Mailprogramm
eingerichtet ist, kann der vollständige Entwurf kopiert werden. Es gibt keinen
Formularserver, keine Speicherung der Eingaben und keinen automatischen
Lizenzversand. Die ursprünglichen Formularfelder sind aus den kaputten
Platzhaltern nicht wiederherstellbar; die neuen Felder wurden anhand des
jeweiligen Anfragezwecks rekonstruiert. Die Links zur kostenlosen Lizenz führen
direkt zum Formular.

Der Blog-Link und der alte
`/terms-of-use`-Link innerhalb der Datenschutzerklärung zeigen die Fehlerseite
des Originals. Die aktuelle Nutzungsbedingungen-Seite ist separat enthalten.

Vimeo-Videowiedergabe, externe Zielseiten und der Download des etwa **412 MB**
großen ezuno-Installationspakets benötigen Internet. Das Installationspaket bleibt
mit der Originaladresse verknüpft und ist nicht Bestandteil dieser Website.
Die Gestaltung, Bilder und Schriften sowie die lokalen Seiten funktionieren
auch ohne Internet. Vimeo wird wie im Original als externer Player eingebettet.

## GitHub Pages

Repository: [DavidNemecek/www-ezuno](https://github.com/DavidNemecek/www-ezuno)

Adresse der Veröffentlichung:
[davidnemecek.github.io/www-ezuno](https://davidnemecek.github.io/www-ezuno/)

Die Veröffentlichung verwendet in **Settings → Pages** die Einstellung
**Deploy from a branch**, Branch **`main`**, Verzeichnis **`/ (root)`**.
Die enthaltene `.nojekyll` deaktiviert Jekyll. Eine zusätzliche Build-Pipeline
ist nicht nötig. Weitere Änderungen werden nach einem Push auf `main`
automatisch veröffentlicht.

## Erfassung und Prüfung

`snapshot.json` listet die Seiten und die Zuordnung der Originalressourcen zu den
lokalen Dateien. `tools/mirror.py` erzeugt die Momentaufnahme mit einzeln
ausgeführten, mindestens 1,5 Sekunden auseinanderliegenden Abrufen. Bereits
geladene Dateien werden in `.mirror/` zwischengespeichert. Zum erneuten Erstellen
werden Python 3, Beautiful Soup, lxml und curl benötigt; diese Werkzeuge sind
keine Laufzeitabhängigkeiten der Website.

```sh
python3 tools/mirror.py            # Erfassung mit Cache
python3 tools/mirror.py --offline  # nur aus vorhandenem Cache neu erzeugen
python3 tools/check_links.py       # lokale Verweise prüfen, ohne Netzwerk
```
