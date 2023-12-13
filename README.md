# Safaric

Git-Repository für das Praxisprojekt in Zusammenarbeit mit Safaric Consulting im Rahmen des Capstone Projekts der Universität zu Köln


# Zum Starten müssen folgende Schritte durchgeführt werden:
1. git Repository clonen
2. Pythonversion: 3.7.6
3. Virtuelle Umgebung mit Python aufsetzen
4. für Windows-User: Poppler über http://blog.alivate.com.au/poppler-windows/ (v0.68.0_x86) herunterladen, extrahieren und den bin Ordner im System Path einfügen (mehr Hinweise unter: https://stackoverflow.com/questions/18381713/how-to-install-poppler-on-windows)
5. für Windows-User: Tesseract über https://digi.bib.uni-mannheim.de/tesseract/ (v4.1.0.20190314) herunterladen extrahieren und den Ordner dem Systems Path hinzufügen 
6. für Windows-User: geckodriver über https://github.com/mozilla/geckodriver/releases (v0.29.0) herunterladen den Ordner in dem die .exe datei liegt im System Path einfügen
5. für Mac-User: Installation von Tesseract und Poppler über homebrew: `brew install tesseract --all-languages`, `brew install poppler`; geckodriver über https://github.com/mozilla/geckodriver/releases (v0.29.0)
6. Pfad zum Geckodriver unter safaric/safariv/crawler/views.py in Zeile 192 bei gecko_path'' anpassen
7. in den Ordner safaric/safaric/ navigieren und folgende Befehle zum Starten im Terminal ausführen:
`pip install -r requirementsvenv.txt`,
`python manage.py makemigrations`,
`python manage.py migrate`,
`python manage.py runserver`
8. Unter http://localhost:8000/ kann die Website aufgerufen werden, der Adminbereich ist mit http://localhost:8000/admin zu erreichen
8. Zugangsdaten: Name: admin, Passwort: admin
8. falls später Fehlermeldung "AttributeError: module 'tensorflow' has no attribute 'gfile'" auftritt, muss in der Datei label_map_util.py in Zeile 132 tf.gfile.GFile mit tf.io.gfile.GFile ersetzen (die Datei befindet sich in dem Virtualenvironment-Ordner unter python(Versionsnummer)/site-packages/object-detection/utils)



# Beschreibung der Aufgaben des 4. Sprints
Im vierten Sprint haben wir uns vor allem mit Aufgaben beschäftigt, deren Ergebnisse sich nicht im Repository wiederspiegeln.
Daher hier eine kleine Erklärung:
1. **Aufsetzen des Servers:**
Das Aufsetzen des Servers umfasste folgende Aufgaben:
- Aufsetzen einer Firewall
- Transfer des Programmcodes auf den Server
- Installation von python und einrichten einer virtualenvironment (mit allen Abhängigkeiten)
- Installation von Apache2
- Anpassung der Programmsettings (Allowed Hosts, Pfad von statischen/media files)
- Erstellung einer Apache Konfiguration (Alias für statische/media files, Definition vom wsgi-entrypoint)
- Konfiguration vom WSGI-Daemon-process
- Verwaltung von Zugriffsrechten auf Ordner (chown, chmod)
- Auslagerung von sensiblen Daten (bsp.: secret Key) in eine separate json-Datei
- Installtion von Tensorflow
- Installation von Tesseract
- Installation von geckodriver 
- Aufsetzen einer MariaDB
- Anbindung der Datenbank an die Webapp
- Absicherung durch .htaccess 

Lösung von Problemen (besonders zeitaufwendig):
- Probleme bei der Konfiguration von apache mit nginx
- Konflikte zwischen numpy und apache mod_wsgi
- geckodriver brauchte Zugriffsrechte auf /var/www/

Zusätzliche Hürde:
- eingeschränkter Zugriff auf die Plesk-Oberfläche

2. **ObjectDetection mit der Tensorflow API:**
Nachdem sich mehrere Teammitglieder längere Zeit in die Thematik des Machine Learning in Kombination mit Object Detection eingearbeitet haben, wurde zunächst mit dem Installieren von Tensorflow und der ObjectDetection API begonnen. Danach mussten zunächst die Trainingsdaten eingenhändig erstellt werden und anschließend passend in tfrecord Dateien umgewandelt werden. 
Im nächsten Schritt wurde die API passend konfiguriert und eine Labelmap wurde erstellt. 
Danach folgte die Suche nach dem richtigen vortrainierten Modell. Dafür wurden über einen langen Zeitraum immer wieder neue Modell aus dem Tensorflow Modelzoo ausgewählt und versucht zu trainieren. Bei vielen Schlug das Training sofort fehl, bei anderen reichten die Kapazitäten unserer Hardware nicht aus. Schlussendlich fanden sich einige Modelle, die sich trainieren ließen, wobei jedoch bei manchen der Loss ziemlich schnell auf nan ging. Ein Modell stellte sich dann zum Glück als brauchbar heraus, da nach über 24 Stunden Training der Loss unter 1 fiel und stetig weiter sank. Die restliche Zeit verbrachte das Team damit, zu recherchieren wie das trainierte Modell in die Webapp mit eingebaut werden kann. 


# Testing

### System-Tests

### 1. Sprint:
- US:1.0.1 & US:1.0.2: Passwort wird abgefangen wenn leer, zu ähnlich zu Nutzername, weniger als 8 Zeichen, gleich dem alten
                     Passwort und nur Zahlen -- Bestanden.
- US:1.1.1: Erstellen von Profilen: Leere Eingaben werden abgefangen -- Bestanden.
- US:1.2.1: Hochladen: Wenn Datei im falschen Format → Hinweis auf falsches Format -- Bestanden.
- US:1.2.2: Löschen möglich -- Bestanden.
- US:1.2.3: Vorschau sichtbar -- Bestanden.
- US:1.2.4: Wenn falscher Dateiname → Hinweis auf falschen Dateiname -- Bestanden.
- US:1.3.2: Profil erstellen möglich + Kundenprofile können Händler zugeordnet werden -- Bestanden. 
- US:1.4.1: Vorschau bei Kategorisierung und Auswertung sichtbar -- Bestanden.
- US:1.4.2: Auswerten der Seitennummer → nur eintragen von Zahlen möglich -- Bestanden.
- US:1.4.3: Seitentyp kann eingetragen werden -- Bestanden.
- US:1.4.4 & US:1.4.5: Auswertung der Artikelanzahl (Hauptkategorie u. nicht Hauptkategorie)  → nur eintragen von Zahlen möglich 
                     -- Bestanden.
- US:1.4.6: Bearbeiten von Seiten- und Produktkategorien → leere Eingaben werden abgefangen -- Bestanden.
- US:1.5.1: Auswerten eines Hero-Artikels möglich -- Bestanden.
- US:1.5.2: Auswerten einer Artikelkategorie möglich -- Bestanden.
- US:1.5.3: Seitentyp kann eingetragen werden -- Bestanden.
- US:1.6.1: Auswerten des Artikelnamens → leere Eingaben werden abgefangen -- Bestanden.
- US:1.6.2: Auswerten des Preises → nur eintragen von Zahlen möglich -- Bestanden.
- US:1.6.3: Auswerten des Aktion Typs → leere Eingaben werden abgefangen -- Bestanden.

### 2. Sprint:
- US:2.1.1: Kategorien bearbeiten durch den Admin möglich -- Bestanden.
- US:2.2.1: Import über pdf und jpg Dateiformate möglich -- Bestanden.
- US:2.3.2: Administratoren ist es möglich Händler- und Branchenprofile eines Kundenprofils zu verändern und ggf. zu löschen 
          -- Bestanden.
- US:2.3.3: Veränderung von Parametern durch den Admin möglich -- Bestanden.
- US:2.5.1: Administrator ist es möglich Seiten- oder Produktkategorien zu bearbeiten -- Bestanden.
- US:2.5.2: Nutzer sieht Vorschau der Seite und kann Seite in Artikelbereiche unterteilen -- Bestanden.
- US:2.6.1: Dropdown Menü und Autovervollständigung funktioniert -- Bestanden.
- US:2.6.2: Administrator kann Anreizkategorien bearbeiten -- Bestanden.
- US:2.7.1: Aufrufen der Dashboard-Seite ist möglich -- Bestanden.
- US:2.7.2: Auswertungsergebnisse als Exceldatei zu exportieren ist möglich -- Bestanden.
- US:2.7.3: Auswertungsergebnisse sind für Kunden sichtbar -- Bestanden.

### 3. Sprint:
- US:3.2.1: Automatischer Import von ausgewählten Händlern ist möglich -- Bestanden.
- US:3.7.1: Auswertungsergebnisse der aggregierten Anzahl je Kalenderwoche einsehbar -- Bestanden.
- US:3.7.2: Durchschnittswerte der Händler können  in den Auswertungsergebnissen gefiltert werden -- Bestanden.
- US:3.7.3: Durchschnittswerte pro Zeitraum über die gefilterten Händler sind einsehbar -- Bestanden.
- US:3.7.4: Einsehen der Auswertungsergebnisse in tabellarischer Form möglich -- Bestanden.
- US:Z3.1: Bild der Handzettelseite wird zur Übersicht auch in der Artikelauswertung angezeigt -- Bestanden.
- US:Z3.2: Artikelbilder bewegen sich beim Scrollen in der Auswertung mit und sind permanent sichtbar -- Bestanden.
- US:Z3.3: Seitenkategorie wird für die Artikelauswertung übernommen -- Bestanden.
- US:Z3.4: Reine Handzettel-Seitenauswertung ist möglich -- Bestanden.
- US:Z3.5: Fertige Artikelauswertungen können durch anwählen der Checkbox bei der Artikelauswertung kenntlich gemacht werden 
         -- Bestanden. 
- US:Z3.6: Fortschrittsanzeige für die Auswertung einsehbar -- Bestanden.
- US:Z3.7: Handzettel, bei denen die Seitenauswertung abgeschlossen wurde, werden bei den Auswertungsergebnissen berücksichtigt 
         -- Bestanden.

### 4. Sprint:
- US:3.4.1: KI macht Vorschlag für Anzahl der Produkte innerhalb einer Seitenproduktkategorie -- Bestanden.
- US:3.4.2: KI macht Vorschlag für Artikelseite -- Bestanden.
- US:3.4.3: KI macht Vorschläge zur Einteilung der Artikel Platzierungen -- Bestanden.
- US:3.4.4: Vorschläge der KI werden mit der Zeit besser/präziser -- Bestanden.
- US:3.4.5: Hinweise, in Prozent, wie sicher die KI über die Richtigkeit des Vorschlags in der Seitenauswertung ist -- Bestanden.
- US:3.5.1: KI macht Vorschläge zur Aufteilung in Artikelbereiche -- Bestanden.
- US:4.4.1: Nutzer erhält von KI Kategorisierungsvorschlag mithilfe Dictionarys -- Bestanden.
- US:4.5.1: Hinweise, wie sicher die KI über die Richtigkeit des Vorschlags in der Artikelauswertung ist -- Bestanden.
- US:4.6.1: KI macht Vorschlag zur Auswertung des Preises -- Bestanden.
- US:4.7.2: Auswertungsergebnisse werden tabellarisch dargestellt -- Bestanden.
- US:4.7.3: Anwendung von Filtern in den Auswertungsergebnisse möglich -- Bestanden.
- US:Z4.1: Seitenauswertung ist direkt ohne die Kategorisierung der Artikel möglich -- Bestanden.
- US:Z4.2: Crawl-Prozess per Abbruch-Button abbrechen oder abschließen möglich -- Bestanden.

- US:Allgemein: Webanwendung soll auf dem von Safaric zur Verfügung gestellten Server online zugänglich sein -- Bestanden.


### Unit-Tests

In dem Tests-Ordner des Projektes wurden 19 verschiedene Unit-Tests implementiert. Diese sind wiederum in URL-Tests und View-Tests unterteilt. Das Testing wurde durch die GitLab CI/CD-Pipeline automatisiert. Somit werden alle Testfälle bei Veränderungen im Master-Branch abgearbeitet.  

**URL-Tests:** Durch die URL Tests wird geprüft, ob bei dem Aufruf der jeweiligen URL die erwartete View aufgerufen wird, die wiederum ein entsprechendes Template rendert.

Folgende Testfälle wurden implementiert:

- test_home_url_resolves
- test_handzettelliste_url_resolves
- test_ausw_handzettelliste_url_resolves
- test_handzettelauswertung_url_resolves
- test_ergebnisse_url_resolves
- test_seitenauswertung_url_resolves
- test_artikelauswertung_url_resolves
- test_uploadhandzettel_url_resolves



Bei der Benennung der Test wurde folgendes Muster eingehalten: test_< Name der View die aufgerufen werden soll>_url_resolves

**View-Tests:** Durch die View-Tests wurde jeweils eine GET-Anfrage durch den Client simuliert. Dabei wurde zum einen ein Zugriff durch einen eingeloggten Nutzer und zum anderen ein Zugriff durch einen nicht eingeloggten Nutzer simuliert. 
Bei den Tests wurde jeweils geprüft, ob die durch den Nutzer über die URL aufgerufene Seite zugreifbar ist (HTTP-Statuscode 200) oder dieser, falls der Nutzer nicht eingeloggt sein sollte, auf den Login weitergeleitet wird (HTTP-Statuscode 302). Zudem wurde geprüft, ob beim Laden der jeweiligen Seite auch das richtige Template gerendert wird.

Folgende Testfälle wurden implementiert:

- test_home_GET
- test_handzettel_list_GET
- test_ausw_handzettel_list_GET
- test_ergebnisse_GET
- test_handzettel_list_GET_ohne_login
- test_home_GET_ohne_login
- test_ergebnisse_GET_ohne_login
- test_seite_GET_ohne_login
- test_artikel_GET_ohne_login
- test_upload_GET_ohne_login
- test_ausw_handzettelliste_GET_ohne_login


Bei der Benennung der Testfälle wurde folgendes Muster eingehalten:

Test bei denen der Nutzer eingeloggt ist:

Test_< Name der Seite die geladen werden soll>_GET

Tests bei denen der Nutzer nicht eingeloggt ist:

Test_< Name der Seite die geladen werden soll>_GET_ohne_login


## Verwendete Software

Name:               Version:            Lizenz:

bootstrap           4.3.1               MIT

jquery              3.5.1               MIT

pdf2image           1.14.0              MIT   

poppler             0.68.0              GNU GPLv2   

pytesseract         0.3.7               Apache 2.0

tesseract           4.1.1               Apache 2.0

jcrop                                   MIT 

tensorflow          2.4.1               Apache License 2.0

Django              3.1.5               BSD License

Selenium            3.131.0             Apache License 2.0

urllib3             1.26.2              MIT

pdf-crawler                             MIT

geckodriver         0.29.0              Mozilla Public License






