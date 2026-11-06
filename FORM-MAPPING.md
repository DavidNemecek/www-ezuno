# E-Mail-Buttons statt Formularen

Geprüft am 6. November 2026. Grundlage ist der lokale historische Export
`../backup/ezuno.com/transfer/wordpress_1.sql`, Tabellen `wp_posts` und
`wp_postmeta`. Untersucht wurden ausschließlich die Formular-Konfigurationen;
der Datenbankexport wird weder veröffentlicht noch für den Website-Build benötigt.

## Wiedergefundene Originalvorlagen

| Formular | Originale Eingaben | Ursprünglicher Empfänger | Ursprünglicher Betreff |
| --- | --- | --- | --- |
| 319, FREE BASIC | E-Mail-Adresse (`email-567`) | `sales@ezuno.com` | `ezuno - FREE BASIC Request` |
| 323, Kontakt / Angebot | Name (`your-name`), E-Mail (`your-email`), Nachricht (`your-message`) | `sales@ezuno.zendesk.com` | `ezuno.com - Contact Us` |
| 4449, Support | Im bereitgestellten Export nicht enthalten | Nicht rekonstruierbar | Nicht rekonstruierbar |

Die Konfigurationen 319 und 323 stehen jeweils unter den Metaschlüsseln `_form`
und `_mail`. Beide verwendeten `forms@ezuno.com` als technischen Absender und
die eingegebene Besucheradresse als `Reply-To`; diese technischen Header werden
bei `mailto:` durch das eigene Mailprogramm ersetzt. Es gab keine Anhänge, keine
HTML-E-Mail und keine aktive zweite Bestätigungsnachricht (`_mail_2`).

Die FREE-BASIC-Nachricht enthielt die angegebene E-Mail-Adresse und die Bitte um
einen Lizenzschlüssel für den FREE-BASIC-Plan von ezuno. Die Kontakt-Nachricht
enthielt Name/E-Mail sowie die Nachricht. Ihr ursprünglicher Eingabehinweis fragte
nach der benötigten Benutzeranzahl, einer laufenden FREE-BASIC-Evaluierung und
einer Evaluierung mit mehr als zehn Benutzern. Diese drei Fragen stehen nun als
Ausfüllhilfe im E-Mail-Text. Firma, Anliegen-Auswahl und Versionsnummer waren
für diese Originalvorlagen nicht belegt. Die nun auf Betreiberwunsch neu
geschriebenen E-Mail-Entwürfe ergänzen Firma optional und technische Angaben
bei Supportanfragen; dies sind neue Ausfüllhilfen.

Die Formulare 3468 (unverändertes Standardformular), 3851 (Test) und 3854
(Backup-Kopie) sind ebenfalls im Export vorhanden. Die öffentlichen,
veröffentlichten Seiten des Exports referenzieren davon keines; ihre internen
und Demo-Empfänger werden deshalb nicht als neue Website-Kontaktziele verwendet.

## Grenze der Support-Rekonstruktion

Das Support-Dokument vor dem Umbau verweist auf das frühere Formular 4449.
Dieser Datensatz fehlt im älteren SQL-Export. Die vorhandene
[Endbenutzer-Lizenzvereinbarung](ezuno-end-user-license-agreement-eula/index.html)
nennt im Abschnitt zu Supportanfragen ausdrücklich `support@ezuno.com` und
verlinkt diese Adresse mit `mailto:`. Für die neuen Website-Buttons hat der
Betreiber am 6. November 2026 ausdrücklich `ezuno@ezuno.com` gewählt.
Die neue Supportvorlage fragt nach Problem, erwartetem Verhalten, Schritten zur
Reproduktion, ezuno-/Alfresco-Version, Betriebssystem und Fehlermeldung.
Dies ist keine Rekonstruktion der historischen Felder von Formular 4449.

## Ältere Gravity-Forms-Konfigurationen

Der Export enthält außerdem frühere Gravity-Forms-Definitionen für kostenlose
Lizenzen, Newsletter, Kontakt, Bestellungen und Enterprise-Angebote. Die
entsprechenden produktiven Formulare sind in `wp_rg_form` als inaktiv markiert;
die noch als aktiv markierten Test-/Entwurfsformulare liegen im Papierkorb.
Eine Support-Definition ist auch dort nicht vorhanden. Die aktuelle Website
verlinkt ihre Lizenz- und Verkaufs-CTAs auf die Abschnitte der CF7-Formulare
319 und 323. Die älteren Gravity-Forms-Abrechnungs-, Adress- und
Lizenzgeneratorfelder werden deshalb nicht als aktuelle Eingaben übernommen.

## Umsetzung

Die geprüften Vorlagen stehen in [`tools/static_forms.py`](tools/static_forms.py).
Nur die bisherigen sieben Formularstellen sind durch einfache `<a href="mailto:…">`
Buttons mit Vorlage ersetzt. Alle drei Vorlagen gehen an `ezuno@ezuno.com`.
Die Texte stehen in [`EMAIL-TEMPLATES.md`](EMAIL-TEMPLATES.md).
Die FREE-BASIC-, Bestell- und Angebots-CTAs führen zu diesen Abschnitten.
Gewöhnliche E-Mail-Links bleiben einfache Kontaktlinks ohne Vorlage.
Auf der Website gibt es keine Formularfelder, keinen
Entwurfseditor, keine Clipboard-Funktion und keine Formular-JavaScript-Abhängigkeit.

Betreff und Nachricht sind getrennt URL-kodiert; Zeilenumbrüche sind CRLF
(`%0D%0A`). Die Besucher ergänzen ihre Angaben und senden die Nachricht selbst
in ihrem Mailprogramm. Die Website selbst versendet und speichert keine Anfrage.
