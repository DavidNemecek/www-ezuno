# Prüfung der statischen Kopie

**Ergebnis des Originalvergleichs vom 30. Oktober 2026: Der unabhängige Subagent
hat keine verbleibenden sichtbaren oder funktionalen Unterschiede festgestellt.**
Die später ausdrücklich gewünschten Verbesserungen sind unten separat dokumentiert.

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
und Fehlerseiten wurden beim ursprünglichen Vergleich als Referenzverhalten
übernommen. Die Formulare wurden am 31. Oktober auf ausdrücklichen Wunsch ersetzt.

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

## Rekonstruierte Formulare

Am 31. Oktober 2026 wurden die drei defekten Formulararten für die kostenlose
10-Benutzer-Lizenz, Kontakt/Angebote und Support an allen sieben Stellen ersetzt.
Die historischen Felder sind im Original nicht mehr sichtbar; die neuen Felder
wurden anhand des Anfragezwecks ergänzt. Die Gestaltung verwendet die vorhandene
Typografie und Farben, mit zwei Spalten auf dem Desktop und einer auf kleinen
Bildschirmen. Links zur kostenlosen Lizenz führen jetzt direkt zum Formular.

Der ausdrücklich gewählte Versandweg ist eine vorausgefüllte E-Mail an
`ezuno@ezuno.com`. Die Website versendet keine Nachricht selbst und meldet keinen
erfolgreichen Versand. Besucher senden den Entwurf im eigenen Mailprogramm ab.
Der Entwurf bleibt zusätzlich lesbar und kopierbar, falls kein Mailprogramm oder
kein Clipboard-Zugriff verfügbar ist. Eingaben werden weder im Browser gespeichert
noch an einen Formularserver übertragen. Native Pflichtfeld- und E-Mail-Prüfung
erfolgt vor dem Erstellen des Entwurfs.

Die ergänzenden Funktionstests bestanden **28/28 Formularfälle** über `file://`
und ein simuliertes GitHub-Pages-Unterverzeichnis, jeweils bei 390 und 1440 Pixeln
Breite. Abgedeckt sind alle sieben Formularstellen, fehlende Pflichtfelder,
ungültige E-Mail-Adressen, reine Leerzeichen, Unicode und Sonderzeichen,
Mail-Empfänger und Inhalt, beide Clipboard-Pfade sowie das Verwerfen veralteter
Entwürfe nach einer Änderung. Der Verweischeck bestätigt nun **679 gültige lokale
Verweise**. Ein Offline-Neuaufbau erzeugt bytegenau denselben Stand.

Der erste unabhängige Formularreview fand eine Footerüberlagerung auf der
eigenständigen Kontaktseite sowie falsche Lizenzziele auf Features-/Pricing-Seiten.
Die Kontaktsektion bleibt nun im normalen Dokumentfluss; alle 15 Lizenzlinks
verweisen auf einen vorhandenen Lizenzformularabschnitt. Der gezielte Nachtest
bestand **66/66 Fälle** bei 390/1440 Pixeln über HTTP, `file://` und Projektprefix:
42 reguläre Maus-/Touchzielprüfungen für Formularfelder und Buttons sowie
24 tatsächliche Klicks auf Lizenz-CTAs. Die Feature-Tabs wurden dabei mit Enter
ausgewählt. Der Footer folgt auch einem ausgeklappten Entwurf.

Runde 2 bestätigte diese Korrekturen unabhängig, fand jedoch eine bestehende
Ladeanimation, die ohne JavaScript das neue Fallback verdeckte. Auf den fünf
Formularseiten blendet nun eine `noscript`-Regel ausschließlich diesen Preloader
aus. Der gezielte Nachtest ohne JavaScript besteht **42/42 Fälle** über die drei
Transportarten bei 390/1440 Pixeln: kein verdeckendes Ladeelement, sichtbarer und
anklickbarer direkter E-Mail-Fallback sowie bedienbare Formularfelder.

Die mobile Tabüberlagerung auf der eigenständigen Features-Unterseite ist ein
in Runde 2 separat dokumentierter Bestandsfehler des Originals. Diese Tabs
wurden im Rahmen der Formularrekonstruktion nicht umgestaltet; die Auswahl per
Tastatur und die anschließend angeklickten Lizenzlinks funktionieren.

**Abschließende unabhängige Freigabe des Formularumfangs: JA.** Runde 3 bestätigt
42/42 Fälle ohne JavaScript und 42/42 Fälle mit JavaScript, einschließlich
regulärer Klicks, nativer Validierung, sichtbarem E-Mail-Fallback und korrekt
folgendem Footer. Die früheren Footer- und Lizenzlinkbefunde bleiben geschlossen.
Alle 20 HTMLs wurden unabhängig zweimal offline reproduziert. Keine offenen
Formularbefunde. Der [Reviewbericht](.mirror/forms-review-3.md) und die
Testartefakte liegen im lokalen, nicht veröffentlichten Testcache.

Der aktuelle Stand ist in
[verification-forms-sha256.json](verification-forms-sha256.json) dokumentiert;
die älteren Manifeste bleiben als historische Prüfnachweise erhalten.
