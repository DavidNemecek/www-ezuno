# Lizenzprüfung und Korrekturen des statischen Umzugs

Stand: 6. November 2026. Gegenstand ist die Umstellung der bisherigen
WordPress-/PHP-Website auf den statischen Bestand in diesem Repository.
Die Prüfung ist keine verbindliche juristische Freigabe aller Firmeninhalte
oder der separat angebotenen Produktsoftware.

## Korrigiert

- Alle 20 HTML-Seiten erklären ausdrücklich die Weitergabe der übernommenen
  und bearbeiteten KeySoft-Templatestruktur einschließlich unserer Änderungen
  unter GPL-3.0-only. Herkunft und Änderungsdatum bleiben erhalten. Jede Seite
  verweist mit passenden relativen Pfaden auf den vollständigen GPL-Text und
  die Komponentenübersicht unter `licenses/README.md`.
- Die Komponentenübersicht trennt diese Templatestruktur von eigenständigen
  Firmeninhalten, der unabhängig geschriebenen CSS-/JS-Implementierung und
  den gesondert unter OFL lizenzierten Schriften.
- Beide Seiten mit Nutzungsbedingungen nehmen gesondert lizenzierte
  Bestandteile ausdrücklich von ihren Copyright-Beschränkungen aus. Die
  Komponentenlizenzen gehen den allgemeinen Bedingungen vor. Die Ausnahme
  steht vor den Einschränkungen und verlinkt die Lizenzübersicht.
- Die geänderten Nutzungsbedingungen tragen Version 1.2 vom 6. November 2026.
- `tools/modernize.py` erhält Lizenzzuordnung und Ausnahme bei späteren
  Pflegeläufen. `tools/check_licenses.py` prüft alle 20 Hinweise, beide
  Ausnahmen, die relativen Lizenzverweise, die drei vollständigen Lizenztexte,
  die fünf unveränderten Schriftdateien und den CSS-/JS-Bestand.
- `tools/build_site.py` führt diese Prüfung im fertig zusammengestellten
  Veröffentlichungsbestand aus. Bei einem Verstoß bricht der Build ab;
  das Deployment erhält dann kein neues Website-Artefakt.

## Bereits vorhandene Bereinigung

Der statische Bestand enthält keine WordPress-/Plugin-PHP-Dateien und keine
der alten Theme-/Plugin-Stylesheets oder JavaScript-Pakete. Die einzige
ausgelieferte CSS-/JS-Implementierung liegt in `assets/site.css` und
`assets/site.js`. Die entfernten Iconfonts werden nicht mehr mitgeliefert.
Die unverändert verwendeten Work-Sans-/PT-Sans-Dateien haben vollständige
OFL-1.1-Lizenzen einschließlich Copyright-Hinweisen.

Die vorhandene Betreiberfreigabe für Firmenbilder, Logos, Personenfotos,
Firmentexte und das Installationspaket wird zugrunde gelegt; einzelne
Rechteketten wurden nicht unabhängig geprüft.

## Gesondert zu erledigen oder zu klären

- **Altes Hosting:** Die bisherige WordPress-Installation muss außerhalb der
  öffentlich erreichbaren Serverpfade aufbewahrt oder vom alten Hosting
  entfernt werden. Ein DNS-Wechsel allein garantiert das nicht. Der lokale
  Backupordner wird vom statischen Build nicht veröffentlicht.
- **Git-Historie:** Frühere öffentliche Commits enthalten weiterhin alte
  Theme-/Plugin-Dateien. Die Bereinigung des aktuellen Deployments entfernt
  diese historischen Kopien nicht. Deren Lizenzlage bzw. Bereinigung bleibt
  gesondert zu klären; die Git-Historie wird nicht durch den Build umgeschrieben.
- **Installer:** Bei der vorausgegangenen Stichprobe fehlten in den beiden
  macOS-Paketen die üblichen Lizenzdateien im mitgelieferten Java-Verzeichnis.
  Die x64-Laufzeit identifiziert sich als OpenJDK 11.0.18+10. Die vollständige
  Runtime-Redistributionsprüfung ist unabhängig von den Website-Templates.
  Einige andere Bibliotheken enthalten bereits Lizenz- und NOTICE-Dateien.
- **Hostingbedingungen:** Die konkrete kommerzielle Nutzung ist zusätzlich
  mit den Nutzungsbedingungen des gewählten Hosters abzugleichen.

## Quellen

- [GNU: Lizenzierung von Programmausgaben](https://www.gnu.org/licenses/gpl-faq.en.html#WhatCaseIsOutputGPL)
- [GNU: ausdrückliche Lizenzkennzeichnung](https://www.gnu.org/licenses/gpl-faq.en.html#LicenseCopyOnly)
- [GPLv3, insbesondere Abschnitte 4, 5 und 10](https://www.gnu.org/licenses/gpl-3.0.html)
- [SIL OFL 1.1](https://openfontlicense.org/open-font-license-official-text/)
- [Work Sans: offizieller Lizenztext](https://raw.githubusercontent.com/google/fonts/main/ofl/worksans/OFL.txt)
- [PT Sans: offizieller Lizenztext](https://raw.githubusercontent.com/google/fonts/main/ofl/ptsans/OFL.txt)
- [GitHub Pages: Nutzungsbeschränkungen](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits#usage-limits)

Build- und Deployment-Nachweise stehen in `VERIFICATION.md`; der vollständige
Lizenzkontext des statischen Bestands steht in `LICENSE-REVIEW.md`.
