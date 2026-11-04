# Tumbler-Liniensensor – Schaltung R1 / Layout R2

Schaltung: 14.10.2026; Layout und Montage ergänzt am 18.10.2026. Bearbeitete Grundlage: hochgeladene Datei `Liniensensor.kicad_sch`.
Die hochgeladene Datei enthielt den älteren Aufbau mit J1–J4, ohne Widerstandswerte und ohne die zuletzt besprochenen LS-Labels. Die Sensor- und Treibertopologie sowie die Referenzen U1–U6, Q1/Q2 und R1–R12 wurden beibehalten; die Darstellung wurde neu geordnet. Die UUIDs dieser vorhandenen Bauteile wurden beibehalten.

## Dateien und Verwendung

- `Liniensensor.kicad_sch`: bearbeitbarer KiCad-Schaltplan, Format KiCad 9, auch mit KiCad 10 zu öffnen.
- `Liniensensor.kicad_pro`: Projekteinstellungen mit 0,20 mm Mindestabstand, 0,25 mm Leiterbahnbreite und 0,10 mm Siebdruckabstand.
- `Tumbler_Sensor.kicad_sym` und `sym-lib-table`: mitgeliefertes CNY70-Symbol; zusammen mit dem Projekt im selben Ordner lassen.
- `Liniensensor.pdf`: Ansicht des Schaltplans.
- `Stueckliste.csv`: Einzelbauteile mit Wert, Footprint, Hersteller, Bestellnummer, Belastbarkeit und Datenblatt-Link; Semikolon als Trennzeichen.
- `Pruefung.txt`: Ergebnisse der elektrischen und strukturellen Prüfung.
- Dieses Dokument: Auslegung, Anschlussbelegung und Messungen am Prototyp.

Am einfachsten das vollständige ZIP in einen eigenen Ordner entpacken und `Liniensensor.kicad_pro` öffnen. Bei Übernahme in ein anderes Projekt auch die lokale Symbolbibliothek und ihren Eintrag übernehmen; eine dort bereits vorhandene `sym-lib-table` nicht ungeprüft überschreiben. Das Paket enthält jetzt das vollständig geroutete PCB, lokale Symbol-/Footprint-Bibliotheken, 3D-Modelle und Fertigungsdaten. Die verwendeten offiziellen KiCad-Bibliotheksdateien sind beigelegt. Siehe `Montage_und_Layout.pdf` für Lochbild, Höhe und Halter.

### CNY70-Symbol und ERC

Das offizielle CNY70-Symbol bezeichnet den Phototransistor-Emitter als `open_emitter`. Zusammen mit dem erforderlichen GND-PWR_FLAG führt das zu sechs Pin-Typ-Konflikten, obwohl der direkt geerdete Emitter hier elektrisch richtig ist. Deshalb enthält die lokale Bibliothek eine Kopie mit **Pin 4 als passivem Transistoranschluss**. Geometrie, Pinnummern, Footprint und elektrische Verdrahtung bleiben gleich; der Kollektor bleibt `open_collector`. Es wurden keine ERC-Ausnahmen hinzugefügt und keine Regeln für diese Meldung abgeschaltet.

KiCad 9.0.9 meldet mit den mitgelieferten Projekteinstellungen **0 Fehler, 0 Warnungen, 0 Ausnahmen**. Eine zusätzliche Prüfung mit frischen KiCad-Projekteinstellungen liefert ebenfalls 0 Meldungen. Die native KiCad-Netzliste bestätigt alle sechs LS-Knoten; außerdem wurden LED-Ketten, Stromsenken, Versorgung und sämtliche Footprint-Pinnummern unabhängig abgeglichen. Der Schaltplan wurde als PDF exportiert und visuell auf Überschneidungen und abgeschnittene Inhalte geprüft.

## Anschlüsse

Es bleibt ein Stecker J2: JST GH, 10-polig, seitlicher Kabeleingang, 1,25-mm-Raster. Platinenstecker `SM10B-GHS-TB(LF)(SN)`, Kabelgehäuse `GHR-10V-S`, Crimpkontakte `SSHL-002T-P0.2`. Die Serie ist mit 1 A bei AWG26 spezifiziert; die Sensorversorgung liegt im Normalbetrieb deutlich darunter. Die Haltepads MP sind mechanische Lötflächen, keine zusätzlichen Signalkontakte.

| Pin J2 | Netz | Verwendung |
|---|---|---|
| 1 | GND | Masse |
| 2 | VBAT_SW | Geschützte und geschaltete 2S-Versorgung, Auslegung 6,4–8,4 V |
| 3 | GND | Zweite Masseleitung |
| 4 | +3.3V | Geregelte 3,3 V ±5 % von der Hauptplatine |
| 5 | LS1 | U1, Kollektor Pin 3 |
| 6 | LS2 | U2, Kollektor Pin 3 |
| 7 | LS3 | U3, Kollektor Pin 3 |
| 8 | LS4 | U4, Kollektor Pin 3 |
| 9 | LS5 | U5, Kollektor Pin 3 |
| 10 | LS6 | U6, Kollektor Pin 3 |

Beide Masseleitungen anschließen. Kabel vor dem Einschalten durchmessen: Pin 1 zu Pin 1 usw. Die Pinzählung am Gegenstecker wirkt beim Blick auf die andere Steckseite gespiegelt. Nicht anhand der Aderfarbe annehmen, dass ein fertig gekauftes Kabel richtig belegt ist. Die Nummer am GH-Stecker ist keine ESP32-GPIO-Nummer.

VBAT_SW ist kein Ladeanschluss. Schutz, Ladegerät, Hauptschalter und Regler gehören auf die Hauptplatine. Diese Platine ist für eine bereits begrenzte 2S-Versorgung vorgesehen; Motor-Spannungsspitzen müssen im Gesamtsystem abgefangen werden. Die 25-V-Kondensatoren ersetzen diesen Schutz nicht.

## Eingebaute Bauteile

| Referenzen | Wert / Typ | Gehäuse | Nennwert / Reserve |
|---|---|---|---|
| R1, R9 | 47 Ω | 0805 | 1 %, 0,125 W Standardbetrieb |
| R2, R3, R7, R8 | 1 kΩ | 0805 | 1 %, 0,125 W |
| R4–R6, R10–R12 | 10 kΩ | 0805 | 1 %, 0,125 W |
| R13–R18 | 47 kΩ | 0805 | 1 %, 0,125 W |
| C1, C3 | 100 nF | 0805 | X7R, ±10 %, 50 V |
| C2, C4 | 10 µF | 1206 | X7R, ±10 %, 25 V |
| C5–C10 | 10 nF | 0805 | X7R, ±10 %, 50 V |
| Q1, Q2 | Nexperia BC817-40,215 | SOT-23 | 45 V, 500 mA; 250 mW bei 25 °C, temperaturabhängig reduzieren |
| U1–U6 | Vishay CNY70 | THT | Auslegungsstrom etwa 20 mA je IR-LED |

Widerstände: Vishay CRCW0805, konkrete Bestellnummern in der Stückliste. Obwohl die aktuelle Tabelle auch 0,25 W im erweiterten Betrieb aufführt, wurde konservativ mit 0,125 W im Standardbetrieb gerechnet. Ein Footprint allein definiert keine Belastbarkeit; die Bestellnummer und das Datenblatt des bestückten Bauteils sind maßgeblich.

100-nF-Kondensatoren: KEMET `C0805C104K5RACTU`; 10-nF-Kondensatoren: KEMET `C0805C103K5RACTU`; 10-µF-Kondensatoren: TDK `C3216X7R1E106K160AB`. Die kleinen Kondensatoren wurden mit 50 V gewählt, um eine konkrete, einheitliche Bauteilserie zu verwenden. Die 10-µF-Typen haben 25 V statt der zuvor vorgeschlagenen 10/16 V. X7R-Kapazität sinkt mit Gleichspannung, Temperatur und Alterung; 10 µF ist der Nennwert, kein garantierter Mindestwert bei 8,4 V. Hier dienen sie der lokalen Abstützung, nicht der Frequenzfestlegung oder einer Reglerkompensation.

## LED-Strom und Verlustleistung

U1/U2/U3 bzw. U4/U5/U6 bilden jeweils eine LED-Reihenschaltung. Q1/Q2 mit R1/R9 sind einfache Stromsenken. Der Strom ist nicht präzisionsgeregelt und verändert sich mit V_BE, Temperatur, Stromverstärkung und 3,3-V-Versorgung.

Mit gleichen 1-kΩ-Basiswiderständen gilt für die unbelastete Basisquelle:

- V_th = 3,3 V / 2 = 1,65 V.
- R_th = 1 kΩ || 1 kΩ = 500 Ω.
- I_C = (V_th − V_BE) / [R_E × (1 + 1/β) + R_th/β].

Beispiel, keine garantierten Datenblattgrenzen: β = 200 und V_BE = 0,65 V ergeben I_C = 20,11 mA. Bei V_BE = 0,70 V sind es 19,10 mA. Damit ergibt sich für jede der drei LEDs einer Gruppe derselbe Strom; beide Gruppen zusammen benötigen ungefähr 40 mA aus VBAT_SW.

Bei 8,4 V, angenommenen 1,25 V LED-Flussspannung und dem ersten Beispiel:

- R1/R9: rund 19,2 mW gegenüber 125 mW Standard-Nennleistung.
- Q1/Q2: rund 74,4 mW gegenüber 250 mW bei 25 °C.
- Jeder 1-kΩ-Basiswiderstand: ungefähr 3 mW; selbst 3,465 V direkt über 990 Ω entsprächen nur 12,2 mW.
- Jeder 10-kΩ-Pull-up: höchstens etwa 1,22 mW bei 3,465 V und 9,9 kΩ.

Ein zusätzlicher Parameterdurchlauf mit **angenommenen**, nicht vollständig garantierten Grenzen (3,3 V ±5 %, R ±1 %, β = 100…600, V_BE = 0,5…0,9 V, LED-V_F = 0,9…1,6 V) ergibt etwa 12,3…26,3 mA, maximal 32,4 mW am Emitterwiderstand und 117,8 mW am Transistor bei 8,4 V. Dieser Durchlauf bewertet die Reserve, ersetzt aber keinen garantierten Temperatur-Grenzfall aus vollständigen Bauteilmodellen. Das BC817-40-Datenblatt spezifiziert seine Verstärkungsgruppe bei anderen Prüfbedingungen als 20 mA.

Bei 60 °C Umgebung verbleiben aus 250 mW und 500 K/W etwa 180 mW zulässige Transistorverlustleistung unter den Referenz-Montagebedingungen. Für den Prototyp deshalb den Bereich 0…60 °C als zu prüfenden Einsatzbereich ansetzen und im geschlossenen Gehäuse messen. Fehlerfälle wie kurzgeschlossene LEDs sind damit nicht qualifiziert.

Bei 6,4 V, konservativ angenommenen 3 × 1,6 V über den LEDs und etwa 1 V am Emitter bleiben circa 0,6 V am Transistor. Unterhalb dieses Versorgungsbereichs kann der Strom abfallen. Die 1,6 V stammen aus einer Datenblatt-Prüfbedingung mit 50 mA und sind keine temperaturübergreifende Garantie für diese Schaltung.

## Ausgangssignal und ESP32-S3

Pro Kanal: Kollektor → 10 kΩ → +3.3V; Kollektor → 47 kΩ → GND; Kollektor → 10 nF → GND. Der Kollektor ist gleichzeitig LS1…LS6. Alle Phototransistor-Emitter gehen direkt nach GND.

- Dunkelwert nominal: 3,3 V × 47 / (10 + 47) = 2,721 V.
- Oberer Dunkelwert bei +5 % Versorgung und ungünstigen 1-%-Widerständen: rund 2,867 V, ohne externe Zusatz-Pull-ups und ohne zusätzliche Störeinkopplung.
- Quellenwiderstand nominal: 10 kΩ || 47 kΩ = 8,246 kΩ.
- Näherung vor Sättigung: U_LS ≈ 2,721 V − I_Photo × 8,246 kΩ.
- Zeitkonstante mit 10 nF: 82,5 µs; Grenzfrequenz circa 1,93 kHz.

Mehr reflektiertes IR-Licht senkt die Ausgangsspannung. Der S3 nennt für die höchste ADC-Dämpfung einen kalibrierten Bereich bis 2,9 V. Der Spannungsteiler hält den stationären Dunkelwert bei den genannten Toleranzen darunter. Dies ist keine Schutzschaltung gegen Fremdspannung. Der untere Bereich nahe Sättigung muss nicht linear messbar sein, um Schwarz und Weiß zu unterscheiden.

Für die Hauptplatine sechs geeignete ADC-Eingänge einplanen; konkrete GPIOs erst mit deren gesamter Pinbelegung festlegen. ADC-Dämpfung, Abtastung und Kalibrierung in der Firmware prüfen. 10 nF ist ein Startwert für die gewünschte Reaktionszeit. Zusätzliche Kapazitäten am ADC und das Kabel verändern die Gesamtzeitkonstante; Messungen mit laufenden Motoren bestimmen, ob mehr Filterung oder ein Puffer nötig ist. Die vorliegenden Dateien bestätigen keine vollständige ADC-Erfassungszeit-/EMV-Auslegung der noch unbekannten Hauptplatine.

## Layout und Prototyp

1. Zwei Kupferlagen mit möglichst durchgehender GND-Fläche verwenden. C1–C4 nahe J2, kurze Massewege. Die sechs Filter möglichst nahe ihren Signalausgängen platzieren.
2. Die Rückströme der ungefähr 20-mA-LED-Gruppen dürfen keine langen gemeinsamen schmalen Leiterbahnen mit den Sensorsignal-Massen teilen. Motorströme gehören nicht auf die Sensorplatine.
3. CNY70-Orientierung anhand der Pin-1-Markierung und der Datenblatt-Ansicht prüfen. Alle Sensoren mechanisch gleich ausrichten und ihre optische Seite zum Boden orientieren. Im Layout: 10-mm-Teilung, 76 × 32 mm PCB, vier 3,2-mm-Bohrungen. Mechanische Höhen und Toleranzen siehe Montagezeichnung.
4. Platine mit Schrauben/Abstandshaltern befestigen; der GH-Stecker trägt keine Platine. Kabel im Gehäuse gegen Zug sichern.
5. Zuerst mit strombegrenztem Labornetzteil testen. 3,3 V und VBAT_SW korrekt anschließen; nicht 8,4 V an Pin 4 legen. Anfangs etwa 100 mA Strombegrenzung für VBAT_SW vorsehen; Ladestrom der Puffer kann kurz begrenzen.
6. Spannung an R1 und R9 messen: I_E = U_R / 47 Ω, I_LED geringfügig kleiner. Rund 0,9–1,0 V entspricht ungefähr 19–21 mA. Bei 6,4 und 8,4 V sowie nach Erwärmung wiederholen.
7. Alle sechs LS-Spannungen über den tatsächlich verwendeten schwarzen und weißen Flächen beim vorgesehenen Bodenabstand messen. Nominal dunkler Grenzwert etwa 2,72 V. Unzureichender Kontrast lässt sich nicht allein durch Kalibrierung beheben.
8. Falls beide Flächen fast 0 V liefern, Pull-up/Pull-down gemeinsam beispielsweise auf 4,7 kΩ/22 kΩ verkleinern. Bei schwachem Signal beispielsweise 22 kΩ/100 kΩ prüfen. Dadurch ändern sich Empfindlichkeit und Filterzeit; erst messen, dann ändern.
9. Mit laufenden Motoren, Kabel in endgültiger Lage und eingebautem Gehäuse nachmessen. Schwarz-/Weißkalibrierung sowie ADC-Konfiguration anpassen. DRC ist ohne Befund abgeschlossen; vor Fertigung Gehäusepassung und Linienbreite prüfen.

## Herstellerquellen

- Vishay CNY70: https://www.vishay.com/docs/83751/cny70.pdf
- Nexperia BC817-Serie: https://assets.nexperia.com/documents/data-sheet/BC817_SER.pdf
- Vishay D/CRCW e3, insbesondere Standard-/Extended-Leistung: https://www.vishay.com/docs/20035/dcrcwe3.pdf
- KEMET 100 nF: https://search.kemet.com/download/specsheet/C0805C104K5RAC7800
- KEMET 10 nF: https://search.kemet.com/download/specsheet/C0805C103K5RAC7800
- TDK 10 µF/25 V: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3216X7R1E106K160AB
- JST GH: https://www.jst-mfg.com/product/pdf/eng/eGH.pdf
- Espressif ESP32-S3, ADC-Tabelle: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf

Alle Werte wurden für diesen Sensorentwurf gewählt. Das ist ein elektrisch geprüftes Schaltplan-/Layoutpaket für den Aufbau und die optische Erprobung; eine Messung am fertigen Roboter wurde nicht durchgeführt.
