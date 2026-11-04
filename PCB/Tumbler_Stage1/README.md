# Tumbler – Schaltplan, Stufe 1 (Signalteil)

Stand: 04.11.2026. KiCad 10. Arbeitsstand zur weiteren Überarbeitung; noch keine Fertigungsfreigabe.

## Änderungen

- An allen Hierarchie-Endpunkten explizite Busgruppen statt undefinierter Gruppenmitglieder:
  - USB: `{DN DP}`
  - I2C: `{SDA SCL}`
  - Motor A: `{AIN1 AIN2 ENCA_A ENCB_A}`
  - Motor B: `{BIN1 BIN2 ENCA_B ENCB_B}`
- J2: zehnpoliger JST GH BM10B-GHS-TBT mit 1:1-Pinbelegung zur funktionierenden Sensorplatine.
- Sechs ADC1-Kanäle für die Liniensensoren. R3/R4/R29–R32: je 100 Ohm in Serie, 0603, mindestens 0,1 W. Die Filter auf der Sensorplatine bleiben maßgeblich.
- Benutzertaster von GPIO9 auf GPIO15; Ultraschall-Echo von GPIO10 auf GPIO16.
- J3 führt nun an seinen bisherigen GPIO6/7/15/16-Anschlüssen LS3/LS4/BTN/ECHO. Diese Pins sind damit belegt und nicht mehr frei erweiterbar.
- R28: bisheriger 5-V-Pull-up entfernt, 10-kOhm-Pulldown nach GND.
- R33/R34: USB-Serienwiderstände je 22 Ohm, 0603, mindestens 0,1 W; im Layout nahe dem ESP32-Modul platzieren.
- Hinweis zu GPIO35–37 präzisiert: Verfügbarkeit hängt von der konkreten Modul-/PSRAM-Variante ab.

## J2 und Software

| J2 | Netz | ESP32-S3 GPIO | ADC |
|---|---|---|---|
| 1 | GND | – | – |
| 2 | VBAT_SW | – | – |
| 3 | GND | – | – |
| 4 | 3.3V | – | – |
| 5 | LS1 | 4 | ADC1_CH3 |
| 6 | LS2 | 5 | ADC1_CH4 |
| 7 | LS3 | 6 | ADC1_CH5 |
| 8 | LS4 | 7 | ADC1_CH6 |
| 9 | LS5 | 9 | ADC1_CH8 |
| 10 | LS6 | 10 | ADC1_CH9 |

BTN = GPIO15, ECHO = GPIO16. Firmware-Zuordnungen müssen entsprechend geändert werden. Ohne Firmware-Projekt wurden keine Softwaredateien geändert. Auf ADC1 die zum Sensor passende Abschwächung und Kalibrierung einstellen (Sensor-Ausgänge unter ca. 2,9 V im vorgesehenen Betrieb).

Das Kabel wird nach Pinnummern 1:1 angeschlossen. Nicht aus der optischen Reihenfolge zweier gegenüberliegender Buchsen auf die Verdrahtung schließen.

## Für Stufe 2 offen

**VBAT_SW an J2.2 hat noch keinen Versorgungspfad.** Es ist bewusst nicht an die ungeschaltete VBAT-Schiene angeschlossen. Schutz und Hauptschalter müssen im nächsten Schritt den passenden 2S-Versorgungsausgang liefern. Bis dahin sind die IR-LEDs der Sensorplatine an diesem Hauptplatinenentwurf nicht versorgt.

Weiterhin offen:

- 2S-Zellen, USB-C-Lader, Zellschutz/Balancing, Verpolschutz, Hauptschalter und sämtliche Strompfade;
- AMS1117/5-V-Schiene und Dioden D1/D3/D5 einschließlich USB-Betrieb und Motorversorgung;
- MPU6050 beibehalten oder LSM6DSV: Der bisherige Entwurf enthält weiterhin LSM6DSV mit LSM6DS3-Symbol. Keine stillschweigende Bauteilentscheidung in Stufe 1;
- bisherigen Motortreiber beibehalten oder TB67H450 wählen, Motor-Blockierstrom, Strombegrenzung, Shuntleistung und Kühlung;
- exakter ESP32-S3-Modulcode, LED-Variante/Logikpegelreserve, Encoder-Ausgangspegel;
- Sicherungskennlinie, Kondensator-Spannungsfestigkeit und vollständige konkrete Stückliste;
- ursprüngliche benutzerdefinierte Tumbler2-Footprints und PCB/Mechanik sind noch nicht vorhanden/geprüft.

Die unveränderten leeren Dateien sensors.kicad_sch und motor_driver.kicad_sch bleiben als ursprüngliche Projektdateien enthalten; die Schaltung liegt weiterhin in peripherals.kicad_sch.

## Quellen

- Espressif: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
- JST GH: https://www.jst-mfg.com/product/pdf/eng/eGH.pdf
- Neu beigelegter GH-Footprint aus der offiziellen KiCad-Footprintbibliothek. Bei installierter Standardbibliothek ist der Footprint bereits unter Connector_JST verfügbar.

Die Rohberichte unter Pruefung enthalten auch Bibliotheks-/Footprintmeldungen der Prüfungsumgebung. Sie sind keine Bestätigung einer fertigungsreifen Gesamtplatine. Die gezielten Netzlistenprüfungen sind separat dokumentiert.
