# Tumbler – elektrischer Entwurf Rev. 2.5

Der ESP32-S3-WROOM-1-N8 (ohne PSRAM) steuert den TB6612FNG weiterhin mit Richtung, PWM und STBY. Der funktionierende Liniensensor behält die bisherigen zehn Steckerkontakte. Der neue Bewegungssensor ist der TDK ICM-42670-P. Acht VL53L0X-ToF-Sensoren (GY-530) hängen über den I²C-Multiplexer TCA9548A (je ein Kanal) und behalten alle die Adresse 0x29. Die Firmware ist nicht Teil dieses Pakets.

## Akku 2S oder 3S (Rev. 2.5)

Die Platine läuft mit den vorhandenen **2S-Akkus** (Auslieferzustand, keine Änderung nötig) oder nach Umbau mit **3S**. Umgeschaltet wird mit vier **0-Ω-Brücken** auf der Unterseite. Sie liegen direkt nebeneinander in einem Siebdruck-Kasten „2S | 3S 0R-Brücken“ unter U16/R67–R69.

> **2S: alle vier 0R (R87, R88, R89, R92) bestückt. 3S: alle vier entfernen – R87 ZUERST!**
> Nie halb umbauen. Bleibt R87 drin und wird ein 3S-Akku gesteckt, liegen 12,6 V am BAT-Pin des BQ25886 (absolut max. 12 V) → Lader defekt. R90 und R91 im Kasten sind normale Widerstände und bleiben immer bestückt. Erst nach dem Umbau einen 3S-Akku stecken.

| Brücke | Funktion | 2S (0R bestückt) | 3S (0R entfernt) |
|---|---|---|---|
| R87 (0603) | PACK_SAFE → CHG_BAT (U12 BAT 13/14, C40) | Lader angeschlossen | Lader abgetrennt, kein USB-Laden |
| R88 (0603) | überbrückt R91 95,3 k in Serie zu R38 165 k (LTC4365 OV) | OV 8,75 V | OV 13,52 V |
| R89 (0603) | überbrückt R90 76,8 k im TPS3700-Teiler | Start 6,42 V / Aus 6,00 V | Start 9,66 V / Aus 9,03 V |
| R92 (1206) | schaltet D14 SMBJ8.5A parallel zu D1 SMBJ13A | Klemmung wie Rev. 2.4 | nur D1 (SMBJ13A) |

**Schutz bei falschem Akku:** In 2S-Stellung bleibt die OV-Schwelle bei 8,75 V. Ein versehentlich gesteckter 3S-Akku wird vom LTC4365 komplett gesperrt, nichts bekommt mehr als 8,75 V. In 3S-Stellung startet ein 2S-Akku nicht (8,4 V < 9,66 V).

**LTC4365 (U8):** Getrennte Teiler für UV (R36/R37) und OV (R38/R39 + R91). R91 ändert nur OV. Schwellen 0,5 V (UV fallend, OV steigend): UV = 0,5 V × (1 + 100 k/10 k) = **5,50 V fallend**, Wiedereinschalten nach UV ca. **5,78 V** (Hysterese des LTC4365) – für 2S und 3S gleich. Bei 3S ist UV nur ein letzter Schutz (1,83 V/Zelle); abgeschaltet wird vorher über den TPS3700 (9,03 V) und die Firmware (9,9 V). OV = 0,5 V × (1 + R_oben/10 k): 2S R_oben = 165 k → 8,75 V; 3S R_oben = 165 k + 95,3 k → 13,52 V (0,9 V über 3S voll).

**TPS3700 (U16), Fahrfreigabe:** INB− (Pin 4) = RUN_SENSE, OUTB (RUN_OKn) wird LOW, wenn INB > V_IT+ = 400 mV, und HIGH, wenn INB < V_IT− = 394,5 mV (typ.). R67 150 k (von PACK_SAFE) und R69 2,7 M (von VBAT_SW) treffen sich in RUN_DIV; von dort R90 (bei 2S durch R89 überbrückt) nach RUN_SENSE, R68 10 k nach GND.

- *Q3 aus:* VBAT_SW liegt über R70 100 k (und die Last) auf ≈ 0 V. R69 wirkt dann als Widerstand nach GND: Thevenin an RUN_DIV U_th = U_P × R69'/(R67 + R69'), R_th = R67 ∥ R69' mit R69' = R69 + R70 = 2,8 M. **Einschalten**, wenn U_th × R68/(R_th + R90 + R68) = 0,400 V, also U_ein = 0,400 V × (R_th + R90 + R68)/R68 × (R67 + R69')/R69'.
- *Q3 ein:* VBAT_SW = PACK_SAFE (bis auf R_DS(on) von Q3). R67 und R69 liegen beide an U_P: R_th = R67 ∥ R69, U_th = U_P. **Ausschalten**, wenn U_P × R68/(R_th + R90 + R68) = 0,3945 V, also U_aus = 0,3945 V × (R67∥R69 + R90 + R68)/R68.
- 2S (R90 = 0): U_ein = 0,4 × 15,24 × 1,054 = **6,42 V**, U_aus = 0,3945 × 15,21 = **6,00 V**. 3S (R90 = 76,8 k): U_ein = **9,66 V**, U_aus = **9,03 V**. Weil R90 hinter dem Knoten von R67/R69 liegt, bleibt das Verhältnis U_ein/U_aus (≈ (R67 + R69)/R69 = 1,056) bei 2S und 3S gleich.

**TVS:** D1 = **SMBJ13A** (VRWM 13 V ≥ 12,6 V, VBR 14,4–15,9 V, VC 21,5 V bei Ipp), immer bestückt. D14 = SMBJ8.5A über R92: bei 2S klemmt sie wie in Rev. 2.4 (VBR ab 9,4 V) unter der 15-V-Grenze des TB6612. Bei 3S muss R92 raus, sonst würde D14 bei 12,6 V leiten. Grenzen ehrlich: Bei vollem Pulsstrom liegt die Klemmspannung der SMBJ13A über 15 V; gegen Rückspeisung schützen vor allem der Akku selbst, C17 und Bremsrampen in der Firmware.

**Spannungsfestigkeit bei 3S (12,6 V + Reserve bis OV 13,5 V):** Q1/Q2 AO4406A V_DS 30 V, V_GS von der LTC-Ladungspumpe (unabhängig vom Akku); Q3 AO4407A V_DS −30 V, V_GS ≈ −12,5 V (max. ±25 V); AP63203/AP63205 V_IN bis 32 V; LTC4365 V_IN bis 34 V; TPS3700 V_DD bis 18 V; F1 (NANO2, 125 V), J1 (JST XH, 250 V / 3 A) – alles in Ordnung. C17 jetzt 220 µF/**25 V**, C63 100 nF/**25 V**, alle anderen Kondensatoren an BAT_RAW/BAT_FUSED/PACK_SAFE/VBAT_SW waren schon 25 V. **Risiko: TB6612FNG** – V_M max. 13,5 V im Betrieb (absolut 15 V), bei vollem 3S nur 0,9 V Reserve. SW4 schaltet nur das Gate-Signal (µA), sieht aber in OFF bis 12,6 V über den offenen Kontakten – Datenblatt des JS202011CQN prüfen.

**Liniensensor an J2.2 (VBAT_SW):** Die IR-LEDs (je 3 × CNY70 in Reihe) hängen an einer Stromsenke (Basisteiler 470 Ω/470 Ω an 3,3 V, R1/R9 = 47 Ω): I_LED ≈ 17,6–20,5 mA – **bei 6,0 V, 8,4 V und 12,6 V gleich**, eine Brücke auf 5 V ist nicht nötig (mit 5 V würde die Kette mit 3 × V_F bis 4,8 V plus ca. 0,96 V Emitterspannung gar nicht sicher laufen). Die Spannungsdifferenz fällt am Transistor ab: bei 12,6 V bis ca. 180 mW. Deshalb hat der Liniensensor ab Layout R3 **BCX56-16 (SOT-89, 250 K/W)** statt BC817 (SOT-23): Sperrschicht bei 60 °C Umgebung ca. 104 °C (max. 150 °C). Details: `PCB/Liniensensor_Redesign/Hinweise.md`.

**Akkumessung BAT_ADC:** Teiler bleibt (100 k/22 k): 12,6 V → 2,27 V, 9,0 V → 1,62 V, 8,4 V → 1,51 V. Bei 3S **ADC-Dämpfung 12 dB** verwenden (6 dB reicht nur bis ca. 1,75 V).

**Firmware:** Akkutyp beim Start erkennen (> 9,0 V = 3S), Abschaltung bei 3,3 V je Zelle (6,6 V / 9,9 V), PWM × 6,0 V / U_Akku, Bremsrampen. Details: `Hinweise_Software_Rev2.5.md`, Entwurf für das GitHub-Issue: `Issue_Software_2S3S_Akku.md`.

## Akku und Betriebsarten

| Schalter / Quelle | Fahrzeug | USB-C |
|---|---|---|
| RUN, gültiger Pack | Q3 gibt Fahrversorgung frei, sofern die RUN-Schwelle erreicht ist | Daten/Programmieren mit Akku, Laden gesperrt |
| OFF, Quelle meldet 1,5 oder 3 A | Fahrversorgung aus | Laden über BQ25886 (keine PD-Verhandlung) |
| OFF, nur USB-Standardstrom oder kein USB | Fahrversorgung aus | Kein Laden |
| Kein Pack, abgeschaltetes BMS oder Eingang außerhalb des Schutzfensters | kein regulärer Fahrbetrieb | kein unterstützter Wiederbelebungsmodus; kein USB-allein-Flashen |

**J1 = JST XH 2-polig (B2B-XH-A, stehend), gleicher Stecker wie bei den vorhandenen 2S-Akkus (7,4 V nominal, 8,4 V voll).** J1.1 (eckiges Pad) = Pack+, J1.2 = Pack−. Polarität des Akkusteckers vor dem ersten Anstecken mit dem Multimeter prüfen (U5/LTC4365 mit Q1/Q2 schützt gegen Verpolung). Nur einen Akku gleichzeitig anstecken. Ein XH-Kontakt ist für ca. 3 A ausgelegt, F1 = 5 A. Bei blockierenden Motoren kann der Stecker warm werden. Die Akkus werden **extern geladen**. Ohne NTC liegt TS des BQ25886 im Kalt-Bereich (R51/R52), daher ist Onboard-Laden automatisch gesperrt. Für späteres Onboard-Laden einen 10-kΩ-NTC (103AT, B = 3435) am Akku zwischen TP8 (NTC) und GND anlöten. Vorher Ladestrom und Temperaturfenster anhand des Pack-Datenblatts prüfen. Die Akkus brauchen eigenen Zellschutz (PCM). Die Platine misst die Einzelzellen nicht. Bis Rev. 2.4 war J1 ein Molex Micro-Fit 4-polig mit NTC-Pin (Backup: Tumbler2_Redesign-backups/vor_JST_XH_Akku_2026-11-18).

**Entladepfad:** J1 → F1 → LTC4365 mit Q1/Q2 → PACK_SAFE → Q3 → VBAT_SW. Hier hängen Motor-VM, J2.2 und beide Buck-Regler. Das sind am Motor und an J2.2 bis zu 8,4 V (2S) bzw. 12,6 V (3S). 5 V und 3,3 V werden separat erzeugt. F1 (5 A träge) ist eine vorläufige Pack-/Leitungssicherung und kein Einzelmotorschutz. SW4 führt nur Steuersignale.

**Zwei Abschaltschwellen:** U16 versorgt sich aus PACK_SAFE und darf Q3 nur in RUN einschalten. R67/R68 = 150 kΩ/10 kΩ, R69 = 2,7 MΩ Rückkopplung, R70 = 100 kΩ Bleeder, R90 = 76,8 kΩ (bei 2S durch R89 überbrückt). Mit 400 mV Einschaltreferenz und typ. 5,5 mV Hysterese: 2S Start ca. 6,42 V / Abschalten ca. 6,00 V, 3S 9,66 V / 9,03 V, jeweils nominal (Rechnung im Abschnitt 2S/3S). Motorlast und Spannungsabfall verschieben das Verhalten; ein zurückfedernder Pack kann oberhalb der Startschwelle erneut anlaufen. STBY bleibt beim MCU-Reset über R35 auf LOW; die Firmware muss nach Unterspannung eine erneute Fahrfreigabe verlangen. Für Lagerung: Pack trennen; OFF trennt die Überwachung nicht vollständig.

**Ladepfad:** BQ BAT (13/14, Netz CHG_BAT) hängt über die Brücke R87 an PACK_SAFE vor Q3 und hinter dem Verpolschutz. Nur bei 2S (R87 bestückt). Unterhalb der Fahrabschaltung ist Laden in OFF weiterhin möglich, solange der LTC4365 den Pack durchschaltet. LTC-Schwellen typisch: UV fallend 5,50 V, erneute Freigabe nach UV ca. 5,78 V; OV steigend 8,75 V (2S) bzw. 13,52 V (3S). Unterhalb der Schutzgrenze oder bei durch das BMS getrenntem Pack ist kein Ladezugriff garantiert. Die Schutzstufe nicht für die Wiederaufladung umgehen.

**USB-Eingang:** NCP361SNT1G (U17) trennt VBUS bei Überspannung und begrenzt Überstrom; typ. OV 5,675 V, OCP 0,75 A. C64 und C27 je 2,2 µF/25 V X7R. Die USB-Logik und U11 liegen hinter U17. U10 wertet das Type-C-Stromangebot aus, U11 schaltet den Eingang des BQ nur in OFF bei geeignetem Angebot frei. J4 D+/D− liegen über U4 und R33/R34 ausschließlich am ESP. U12.1/.24 sind lokal miteinander verbunden (DCP-Signatur), getrennt vom Datenpaar der Buchse; das gibt allein keine Ladeberechtigung.

**Ladeparameter:** R48 200 kΩ → 8,40 V; R50 953 Ω / 3810 Ω/A → 250 mA typ.; R49 2,15 kΩ → 1110/2150 ≈ 0,516 A typische Eingangsgrenze. Der tatsächliche Ladestrom kann bei schwacher Versorgung geringer sein. TS-Netz R51/R52 = 5,23 kΩ / 30,1 kΩ passend zum 103AT-2. D2 zeigt Ladeaktivität, bei Fehler kann STAT blinken. U14/Q5 melden USB an GPIO40 (LOW = vorhanden); der Ausgang steuert nicht den Lader.

## Sensoranschlüsse und Firmware

| Anschluss | Pins auf der Platine | Nutzung |
|---|---|---|
| J8 … J15 | 1 VIN (+5 V), 2 GND, 3 SCLx, 4 SDAx | Lötpads (1,0-mm-Bohrung) für GY-530-Kabel, CH0 … CH7 |
| J2 | 1 GND, 2 VBAT_SW, 3 GND, 4 +3,3 V, 5…10 LS1…LS6 | Liniensensor unverändert; beide MP-Laschen jetzt Masse |
| J5 | 1 +5 V, 2 TRIG, 3 ECHO, 4 GND | Reserve-Leiste (früher Ultraschall HC-SR04); TRIG = 3,3-V-Logik, ECHO über Pegelwandler |
| J6 / J7 | 1 Motor+, 2 GND, 3 Encoder A, 4 Encoder B, 5 +5 V, 6 Motor− | A/B über nichtinvertierenden SN74LVC244A zur MCU |

**ToF-Sensoren (Rev. 2.4):** U15 = TCA9548A (8 Kanäle, Adresse 0x70, A0–A2 an GND, RESET = MUX_RSTn an ESP32-S3 GPIO37, 10 kΩ nach +3,3 V). Acht VL53L0X-Trägerplatinen (GY-530) werden mit Kabeln direkt in Lötpads eingelötet, weil die Sensoren am 3D-Gehäuse befestigt werden:

| Anschluss | Kanal | Steuerbyte | Position |
|---|---:|---:|---|
| J8 | CH0 | 0x01 | vorne |
| J9 | CH1 | 0x02 | rechts vorne |
| J10 | CH2 | 0x04 | rechts Mitte |
| J11 | CH3 | 0x08 | rechts hinten |
| J12 | CH4 | 0x10 | offen (Gehäuse) |
| J13 | CH5 | 0x20 | offen |
| J14 | CH6 | 0x40 | offen (Platinenhinterkante) |
| J15 | CH7 | 0x80 | offen |

Lötpads J8–J15: 1 VIN (+5 V), 2 GND, 3 SCL, 4 SDA – das sind die ersten vier Pins der GY-530 in derselben Reihenfolge. GPIO1 und XSHUT werden nicht gebraucht (Multiplexer statt XSHUT). VIN bleibt auf +5 V, weil die Trägerplatinen einen eigenen Regler haben. Pull-ups: Hauptbus R5/R6 = 2,2 kΩ, je Kanal R59–R66 und R79–R86 = 2,2 kΩ, alle nach +3,3 V (nicht +5 V). Busbetrieb mit 400 kHz vorgesehen; mit der echten Kabellänge die Anstiegszeit prüfen. Alle VL53L0X behalten 0x29; vor jedem Zugriff genau einen Kanal im TCA9548A aktivieren. Die IMU bleibt direkt am Hauptbus (0x68). Strom: ca. 20 mA je ToF aus +5 V (8 Sensoren grob 150–300 mA). Messrate bleibt ≈ 50/s je Sensor (20 ms Timing Budget); 8 Sensoren reihum auslesen ≈ 3 ms Busbelegung.

| Funktion | GPIO |
|---|---|
| I²C SDA / SCL; IMU INT1 | 13 / 14; 12 |
| LS1…LS6 (ADC1) | 4, 5, 6, 7, 9, 10 |
| Motor A Richtung / PWM, Motor B Richtung / PWM, Freigabe | 48 / 47, 41 / 42, STBY 39 |
| Encoder M1 A/B, M2 A/B | 38 / 21, 1 / 2 |
| Ultraschall TRIG / ECHO | 11 / 16 |
| RGB, Taster, USB-Anwesenheit | 8, 15, 40 |
| Akkuspannung BAT_ADC (ADC1_CH2) | 3 |
| UART0 TXD0 / RXD0 (an J3) | 43 / 44 (Modulpins 37 / 36) |
| USB D− / D+ | 19 / 20 |

ICM-42670-P: AD0=GND, AP_CS=3,3 V; INT1=GPIO12. VDD lokal 100 nF + 2,2 µF; VDDIO 10 nF. Neuer Treiber erforderlich; Achsen, Vorzeichen, Skalierung und Abtastrate am Fahrzeug überprüfen. GPIO17/18 sind an J3 weiterhin frei. J3: 1/2 = 3,3 V, 3 = TXD0, 5 = RXD0, 7 = EN, 9 = IO0 (BOOT), 4/11/13/15 = GND; damit ist ein externer USB-UART-Adapter (3,3 V) als Rückfallebene zum Flashen/Loggen möglich.

**Akkuspannungsmessung (Rev. 2.2):** R77 100 kΩ / R78 22 kΩ von VBAT_SW nach GND, C67 100 nF, Abgriff BAT_ADC an GPIO3 (ADC1_CH2, auch bei aktivem WLAN nutzbar). U_ADC = 0,1803 × VBAT_SW: 8,4 V → 1,51 V, 6,0 V → 1,08 V; ADC-Dämpfung 6 dB oder 12 dB, Kalibrierung per esp_adc_cal. Der Teiler hängt hinter Q3 und belastet den Pack in OFF nicht (in RUN ca. 70 µA). GPIO3 ist ein JTAG-Strapping-Pin, wird aber nur bei gesetzter eFuse ausgewertet. U18 akzeptiert 5-V-Encodersignale und liefert 3,3-V-Logik an die MCU; je Eingang 10 kΩ auf Sensor-5 V für Open-Collector-Ausgänge. Der Pegelwandler erhält die Encoder- und Echo-Polarität. Nur Encoder verwenden, deren Ausgänge die 5-V-Pull-ups vertragen. R71 = 220 Ω vor dem ersten LED-Dateneingang; C65 = 22 µF an der 5-V-Kette.

**Ladestrom (bewusst unverändert):** 0,25 A Ladestrom bei ca. 0,52 A Eingangsgrenze sind langsam (2-Ah-Pack: ca. 8–9 h). Eine Erhöhung ist ohne Bauteiltausch nicht sinnvoll: U17 (NCP361) hat eine feste Strombegrenzung von 0,55 A min. / 0,75 A typ. und ist nur für ca. 0,5–0,6 A Dauerstrom ausgelegt. Für schnelleres Laden müsste U17 durch einen USB-Überspannungsschalter mit ≥1,5 A ersetzt und danach R49 (ILIM) und R50 (ICHGSET) neu berechnet werden (R49 = 1110 Ω·A / I_IN, R50 = 3810 Ω/A × I_CHG).

## Prüfungen vor Fertigung und Inbetriebnahme

1. Kabel zu den ToF-Sensoren und Pack festlegen. Modulspannung, Bus-Pull-ups, Spitzenstrom, NTC-Kennlinie, Ladegrenzen und Motor-Stallstrom bei tatsächlicher Packspannung prüfen. Sicherung, Steckerkontakte, Leitungen und TB6612 nach Anlauf-/Blockierstrom und Verlustleistung bewerten.
2. Layout neu aus dem Schaltplan abgleichen. U5-Achsen, J8–J11, U16–U18, neue Passiva platzieren. Leistungsschleifen für BQ und Bucks, USB-Differenzpaar, Wärmeableitung, Masseführung und Abstand zur ESP-Antenne prüfen. C14/C21 direkt an U5-VDD, C15 an VDDIO. C33–C40: effektive Kapazität mit Bias/Kennlinien prüfen (u. a. SYS ≥44 µF, BAT ≥10 µF). Die 192 geprüften Footprint-Padzuordnungen ersetzen diese geometrischen und thermischen Prüfungen nicht.
3. RUN-Schaltgrenzen am strombegrenzten Netzteil ohne Zellen und zunächst ohne Motoren messen: TP1/2/3 sowie 5 V/3,3 V überwachen; bei langsamem und abruptem Spannungsabfall prüfen. Später mit Motoren prüfen, ob Anlauf, Bremsen und Spannungserholung zum Neustart führen.
4. **Ladepfad separat mit einem bidirektionalen Batteriesimulator**, nicht mit einem gewöhnlichen, nicht stromsenkenden Netzteil als Akkuersatz prüfen. Beide Steckrichtungen, Default-/1,5-/3-A-Angebot, RUN/OFF, NTC offen/kurz, abgetrennten Pack, Übergang CV/Termination, Temperaturen und fehlende Rückspeisung messen. Eingangsspitzen vor und hinter U17 beim Stecken prüfen. Einen realen Pack erst nach Abgleich seiner Spezifikation einsetzen.
5. **Rückspeisung beim Bremsen:** Die LTC4365-Überspannungsschwelle liegt bei 2S (8,75 V) nur ca. 0,35 V, bei 3S (13,52 V) ca. 0,9 V über dem Ladeschluss. Mit vollem Pack beide Motoren hart bremsen und reversieren, PACK_SAFE/VBAT_SW am Oszilloskop messen. Bei 3S zusätzlich prüfen, dass VBAT_SW unter 13,5 V (TB6612) bleibt. Trennt der LTC4365 (ESP-Reset), Bremsrampen in der Firmware vorsehen.
7. **2S/3S-Umbau testen:** Am strombegrenzten Netzteil (ohne Motoren) in beiden Stellungen Start/Aus der Fahrfreigabe (TP2/TP3) und die OV-Abschaltung messen. In 2S-Stellung 12,6 V anlegen → LTC4365 muss sperren (TP2 ≈ 0 V). In 3S-Stellung prüfen, dass CHG_BAT (U12 BAT) offen ist.
6. Jeden ToF-Port einzeln und dann alle acht an echten Kabeln testen; SDA/SCL-Flanken, Adressen und Richtung der Sensoren prüfen. Mit angehobenen Rädern IMU, Drehrichtung, Encoderphase, Reset/Standby und Ultraschall testen. Maximalen Strom und thermische Reserve im geschlossenen Gehäuse messen. Kein Prototyp oder Fahr-/Ladeversuch wurde mit diesem Schaltplan durchgeführt.

Datenblätter: [TDK ICM-42670-P](https://invensense.tdk.com/wp-content/uploads/2021/07/DS-000451-ICM-42670-P-v1.0.pdf) · [TI TCA9548A](https://www.ti.com/lit/ds/symlink/tca9548a.pdf) · [BQ25886](https://www.ti.com/lit/ds/symlink/bq25886.pdf) · [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf) · [LTC4365](https://www.analog.com/media/en/technical-documentation/data-sheets/LTC4365.pdf) · [NCP361](https://www.onsemi.com/pdf/datasheet/ncp361-d.pdf) · [SN74LVC244A](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf). Weitere Datenblattlinks stehen direkt an den Bauteilen und in der Stückliste.
