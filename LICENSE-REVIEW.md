# Lizenzprüfung des statischen Umbaus

Stand: 6. November 2026. Diese Dokumentation beschreibt den überprüften
Dateibestand und die getroffenen Maßnahmen; sie ist keine verbindliche
Rechtsberatung oder pauschale Zusicherung für beliebige spätere Änderungen.

## Entfernte Bestandteile

Aus dem aktuellen Website-Bestand wurden sämtliche bisherigen Theme- und
Plugin-Stylesheets und JavaScript-Pakete entfernt. Dazu gehören KeySoft,
Visual Composer/WPBakery, jQuery, Bootstrap, Cookie Law Info und die
zusammengefassten SiteGround-Dateien. Die Nucleo-, Font-Awesome- und
VC-Grid-Schriften sowie die mitkopierten Fugue-/Plugin-Icons wurden entfernt.
Auch unbenutzte Paketbestandteile werden nicht mehr im Verzeichnis `assets/`
aufbewahrt.

Die Darstellung steht jetzt in `assets/site.css`, die Browserinteraktionen in
`assets/site.js`. Beide Dateien wurden für diese statische Website neu
geschrieben. Die 14 einfachen Icons sind eigenständig gezeichnete SVG-Pfade
oder Textsymbole innerhalb des Stylesheets. Es gibt keine Laufzeitbibliothek.

Die wiederverwendeten englischen Firmeninhalte und die HTML-Inhaltsstruktur
bleiben erhalten. Für die von KeySoft übernommene HTML-Hülle bleiben der
Herkunftshinweis, das Änderungsdatum und der originale GPL-v3-Lizenztext erhalten;
die direkt gepflegten HTML-Dateien sind ihre bearbeitbare Quellform. Damit wird
die HTML-Ausgabe nicht als vollständig neu geschriebene Vorlage ausgegeben.
Eine neue Implementierung allein würde fremde Bildrechte oder sonstige Rechte
an Inhalten nicht aufheben.

## Verbleibende Ressourcen

- **Schriften:** fünf unveränderte Work-Sans-/PT-Sans-Dateien unter SIL OFL 1.1.
  Die vollständigen Lizenzen und die Dateizuordnung liegen unter
  [`licenses/`](licenses/README.md).
- **Firmeninhalte:** Produktbilder, ezuno-Grafiken, Kundenlogos und Personenfotos
  stammen aus der bestehenden Website. Der Betreiber hat am 6. November 2026
  ausdrücklich bestätigt, dass diese Inhalte verwendet werden dürfen.
- **Eigene Dateien:** `site.css`, `site.js` und die Pflegeskripte sind die neue
  Implementierung. Es wurde keine pauschale MIT-/GPL-Lizenz über fremde
  Firmeninhalte oder Schriftdateien gelegt.
- **Video:** das bestehende Vimeo-Video bleibt extern eingebunden. Eine
  Verbindung zu Vimeo wird erst durch die bewusste Wiedergabe ausgelöst;
  der Player wird beim Schließen entfernt. Das Video wurde nicht kopiert.
- **Installationspaket:** das vorhandene ezuno-Paket wird mit ausdrücklicher
  Freigabe des Betreibers unverändert öffentlich zum Download bereitgestellt.
  Seine Produkt-/Drittanbieterlizenzen bleiben eigenständig; Schrift- oder
  HTML-Lizenzen dieser Website werden nicht auf das Paket übertragen.
  SHA-256 und Dateigröße stehen in `download-source/manifest.json`.

`snapshot.json` führt nur noch vorhandene Originalressourcen, die beiden neuen
Laufzeitdateien sowie die SHA-256-Werte des aktuellen Assetbestands auf.
Der alte WordPress-Downloader wurde durch reine Offline-Pflege ersetzt,
damit ein späterer Aufruf die entfernten Pakete nicht wieder importiert.

## Veröffentlichung und Git-Historie

Die Bereinigung betrifft den aktuellen Dateibestand. Frühere Commits können
weiterhin die ehemals mitkopierten Theme-/Plugin-Dateien enthalten. Ein
Löschen im neuesten Commit entfernt diese Dateien nicht aus einer bereits
veröffentlichten Git-Historie. Bestehende öffentliche Forks oder Kopien lassen
sich dadurch ebenfalls nicht zurückholen.

`python tools/export_site.py` erstellt deshalb zusätzlich ein ZIP des aktuellen
Website-Bestands **ohne Git-Historie**, private Backups oder Entwicklungsumgebung.
Dieser Export kann für eine frische Veröffentlichung verwendet werden.
Die vorhandene Git-Historie und das entfernte Repository wurden nicht umgeschrieben.

Unabhängig von den Dateilizenzen gelten die Bedingungen des Hostinganbieters.
[GitHub Pages schränkt die Nutzung als kostenloses Hosting für Onlinegeschäfte
und vorwiegend kommerzielle Transaktionsseiten ein.](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits#usage-limits)
Diese Hostingbedingung lässt sich durch einen technischen Umbau nicht ändern.
