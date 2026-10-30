# Prüfung der statischen Kopie

**Ergebnis: Der unabhängige Subagent hat im abschließend geprüften Stand keine
verbleibenden sichtbaren oder funktionalen Unterschiede festgestellt.**

Geprüft am 30. Oktober 2026. Grundlage ist der vollständige unabhängige Bericht
unter [`.mirror/review-round-1.md`](.mirror/review-round-1.md). Rohdaten,
Screenshots, Differenzbilder und Reproduktionsskripte liegen ebenfalls lokal in
`.mirror/`; dieser Erfassungs- und Testcache ist von Git ausgeschlossen.

## Umfang

- Alle **20 HTML-Seiten**, einschließlich aller 16 Inhaltsseiten aus der
  öffentlichen Sitemap des Originals sowie der benötigten Alias-/Fehlerseiten
- Desktop mit **1440 × 900** und Mobilansicht mit **390 × 844**
- Statische Auslieferung über HTTP und direktes Öffnen über **`file://`**
- **204 Vergleichspaare** für Seitenansichten, Cookie-Dialoge, Interaktionen
  und Navigation, einschließlich der ersetzenden Nachtests nach Korrekturen:
  jeweils **0 abweichende Pixel im Pixelmatch-Vergleich**, Schwelle 0,1
- Feature-Tabs, FAQ/Akkordeons, Video-Dialog, Cookie-Einstellungen,
  Consent-Persistenz, Menüs und Navigation zwischen Seiten

Die Originalseiten wurden unter ihren ursprünglichen URLs aus den unverändert
gespeicherten HTML- und Ressourcendateien im Browser ausgeliefert. Dadurch
erforderten die wiederholten Vergleiche keine erneuten Abrufe beim Originalserver.
Animationen und Karussells wurden für die Bildvergleiche synchronisiert.

## Behobene Befunde

Der Prüfer fand zunächst eine fehlende eigenständige Features-Unterseite und
eine falsche Scrollposition beim Wechsel von Support zur Startseite. Die
eigenständigen Unterseiten wurden ergänzt. Die Ankerposition wird nach dem
Layoutaufbau korrekt ausgerichtet.

Die Korrekturen wurden unabhängig nachgetestet. Der zuvor fehlerhafte
Desktop-Sprung zu Clients und der mobile Sprung zu Video bestanden jeweils
**3/3 Wiederholungen über HTTP und 3/3 über `file://`**, mit frischen
Browserkontexten. Alle ergänzten Seiten wurden separat visuell verglichen.

## Weitere Prüfungen und Grenzen

Der lokale Verweischeck bestätigt **658 gültige lokale Verweise in 20 Seiten**
und keine PHP-Dateien. Ein zusätzlicher Funktionstest unter einem simulierten
GitHub-Pages-Unterverzeichnis bestand ebenfalls.

Die ursprünglichen Bildvergleiche umfassten weder die tatsächliche externe
Vimeo-Wiedergabe noch den Inhalt des etwa 412 MB großen
Software-Installationspakets. Der separate Videonachtest ist unten dokumentiert.
Ihre externen Ziele bleiben erhalten. Bereits im Original sichtbare Formular-Platzhalter
und Fehlerseiten wurden unverändert als Referenzverhalten übernommen.

Der ursprüngliche, vom unabhängigen Prüfer gesicherte Stand der 171 überprüften
Dateien ist in [verification-sha256.json](verification-sha256.json) dokumentiert.
Der Abgleich dieser Hashes vor der ersten Übergabe ergab keine Abweichungen.

## Nachprüfung der Videowiedergabe

Nach der Meldung eines sichtbaren, aber nicht startenden Players wurde die
fehlende Autoplay-Berechtigung in der Vimeo-Einbettung ergänzt:
`allow="autoplay; fullscreen; picture-in-picture"`. Dies betrifft ausschließlich
die drei Seiten mit Video und den Exporter, der dieses Attribut nun erzeugt.
Vimeo beschreibt diese Freigabe in seiner
[Hilfe zu Autoplay-Beschränkungen](https://help.vimeo.com/hc/en-us/articles/29677068222737-Troubleshooting-Autoplay-restrictions).

Ein weiterer unabhängiger Subagent testete die tatsächliche, ungemockte
Vimeo-Wiedergabe auf Startseite, Home-Alias und eigenständiger Videoseite,
jeweils über HTTP und `file://`: **6/6 Wiedergabetests bestanden**.
Wiedergabezeit und Anzahl decodierter Videobilder steigen; das Video ist nicht
pausiert, der Ton ist aktiviert und es gibt keinen Medienfehler. Auf den beiden
Startseiten wurden zusätzlich Schließen und erneutes Öffnen erfolgreich geprüft.

Die Darstellung vor dem Videostart ist unverändert. Die Prüfung erfolgte in
Chromium. Der konkrete Stillstand im unbekannten Browser des Nutzers konnte
dort nicht reproduziert werden; die ergänzte Berechtigung ist eine geprüfte
Kompatibilitätskorrektur und keine bestätigte Diagnose seiner Browserumgebung.

Der ergänzende [unabhängige Bericht](.mirror/video-fix/review.md) und seine
Testartefakte liegen im lokalen Testcache. Der nach dieser Korrektur geprüfte
Stand der Laufzeitdateien ist in
[verification-video-sha256.json](verification-video-sha256.json) festgehalten.
