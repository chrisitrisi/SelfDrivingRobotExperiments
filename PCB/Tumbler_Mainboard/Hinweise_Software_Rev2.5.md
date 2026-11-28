# Hauptplatine Rev. 2.5 – Hinweise für die Software

Stand 19.11.2026. Bezieht sich auf `Tumbler_Mainboard` (Schaltplan und Platine Rev. 2.5). Neu gegenüber Rev. 2.4: **Akku wahlweise 2S oder 3S** (Abschnitt „Akku 2S / 3S“). Pinbelegung und ToF-Teil sind unverändert. Firmware-Aufgabe dazu: `Issue_Software_2S3S_Akku.md`.

## Akku 2S / 3S (neu in Rev. 2.5)

Ab Rev. 2.5c ist **3S** (12,6 V voll) die Standardbestückung. Die Variante **2S** (8,4 V voll) nutzt die vorhandenen JST-XH-Akkus. Umgeschaltet wird mit vier 0-Ω-Brücken auf der Unterseite (R87, R88, R89, R92). Für die Firmware heißt das:

| | 2S | 3S |
|---|---|---|
| Spannung am Motortreiber (VBAT_SW) | 6,0 … 8,4 V | 9,0 … 12,6 V |
| Hardware-Fahrfreigabe (TPS3700) Start / Aus | 6,42 V / 6,00 V | 9,66 V / 9,03 V |
| Software-Abschaltung (3,3 V je Zelle) | **6,6 V** | **9,9 V** |
| Laden über USB-C | möglich (nur mit NTC) | **gesperrt** (Lader abgetrennt) |

1. **Erkennung beim Start:** BAT_ADC (GPIO 3) messen, bevor die Motoren laufen (STBY = 0). U_Akku = U_ADC × 122 / 22. **U_Akku > 9,0 V → 3S, sonst 2S.** Sicher, weil ein 3S-Akku erst ab 9,66 V freigegeben wird und ein 2S-Akku höchstens 8,4 V hat. Den Wert einmal beim Start festlegen, nicht im Betrieb umschalten.
2. **ADC-Dämpfung 12 dB** (`ADC_ATTEN_DB_12`) ist jetzt Pflicht. Bei 3S liegen bis 2,27 V am Pin, 6 dB reicht nur bis ca. 1,75 V. Mit eFuse-Kalibrierung (`adc_cali_*`) und Mittelwert über 16–64 Messungen.
3. **Software-Abschaltung bei 3,3 V je Zelle** (2S 6,6 V, 3S 9,9 V). Die Spannung bricht beim Anfahren kurz ein. Daher erst abschalten, wenn der gefilterte Wert (z. B. gleitender Mittelwert über 1–2 s) unter der Grenze liegt. Ablauf: PWM auf 0 rampen, STBY = 0, LEDs rot, nicht selbst wieder anfahren. Die Hardware schaltet erst bei 3,0 V je Zelle ab, die Software soll vorher greifen.
4. **Geschwindigkeit unabhängig vom Ladezustand:** `duty = duty_soll × 6,0 V / U_Akku`, auf 0 … 1 begrenzen. Bei vollem 2S (8,4 V) sind das 71 %, bei vollem 3S (12,6 V) 48 % des Sollwerts. Damit fährt der Roboter mit beiden Akkus gleich schnell wie ein leerer 2S-Akku bei 100 %. Wer mit 3S schneller fahren will, setzt die Bezugsspannung höher (z. B. 9,0 V), dann gilt die Kompensation erst unterhalb dieser Spannung. U_Akku dafür gefiltert (z. B. alle 10 ms, Mittel über 100 ms) verwenden.
5. **Bremsrampen (wichtig bei 3S):** Der TB6612FNG ist bis **13,5 V** spezifiziert (absolut 15 V). Ein voller 3S-Akku hat 12,6 V, beim harten Bremsen oder Umpolen speisen die Motoren zurück. Deshalb nie direkt von vorwärts auf rückwärts schalten. PWM in ≥ 100 ms auf 0 rampen, dann erst die Richtung wechseln. Bremsen bei dieser Platine: U7 erzeugt IN2 immer als invertiertes IN1, IN1 = IN2 = HIGH ist also nicht möglich. **Kurzschlussbremse = PWM LOW bei STBY HIGH** (Richtung egal), **Freilauf = STBY LOW**. Kurzschlussbremse nur bei kleiner Drehzahl. Beim Test mit vollem 3S-Akku VBAT_SW (TP3) beim Bremsen mit dem Oszilloskop messen: Spitzen sollen unter 13,5 V bleiben.


## Wichtig vorab: anderer Controller

Die Vorgaben für die ToF-Sensoren wurden für den **ESP32-WROOM-32E** der alten Platine geschrieben. Auf der neuen Platine sitzt ein **ESP32-S3-WROOM-1-N8** (8 MB Flash, kein PSRAM). Deshalb passen GPIO-Nummern und die Liste der zu meidenden Pins nicht 1:1:

| Thema | alter ESP32 | ESP32-S3 (neue Platine) |
|---|---|---|
| I²C SDA / SCL | 21 / 22 | **13 / 14** |
| intern vom Flash belegt | 6–11 | 26–32 (nicht herausgeführt) – **GPIO 6–11 sind frei nutzbar** |
| Strapping-Pins | 0, 2, 5, 12, 15 | **0, 3, 45, 46** |
| nur Eingang | 34, 35, 36, 39 | keine |
| Programmieren | UART 1/3 | **natives USB an GPIO 19/20**; UART0 (GPIO 43/44) liegt zusätzlich an J3 |

Die alte Firmware ist also nicht direkt lauffähig: neu für ESP32-S3 bauen und alle Pins neu zuweisen.

## Umsetzung der ToF-Vorgaben

1. **I²C-Pull-ups** liegen an **+3,3 V**, nicht an +5 V. Wert **2,2 kΩ**: R5/R6 am Hauptbus und R59–R66, R79–R86 an allen acht Kanälen. 400 kHz sind vorgesehen.
2. **Multiplexer TCA9548A** (U15, 8 Kanäle) ist eingebaut:
   - Adresse **0x70** (A0–A2 an GND).
   - RESET (MUX_RSTn) liegt an **GPIO 37** und über 10 kΩ an +3,3 V. Beim Start als Ausgang HIGH setzen; zum Zurücksetzen kurz LOW.
   - Nach dem Einschalten sind alle Kanäle getrennt.
3. **Acht VL53L0X (GY-530)** hängen an Kabeln, die direkt in die Platine gelötet werden (die Sensoren sitzen später am 3D-Gehäuse). Die Lötpads haben die Reihenfolge der GY-530: **1 VIN (+5 V), 2 GND, 3 SCL, 4 SDA**. GPIO1 und XSHUT werden nicht angeschlossen.

| Lötpads | Kanal | Steuerbyte an 0x70 | Einbauort |
|---|---:|---:|---|
| J8 | 0 | 0x01 | vorne |
| J9 | 1 | 0x02 | rechts vorne |
| J10 | 2 | 0x04 | rechts Mitte |
| J11 | 3 | 0x08 | rechts hinten |
| J12 | 4 | 0x10 | noch offen |
| J13 | 5 | 0x20 | noch offen |
| J14 | 6 | 0x40 | noch offen (Hinterkante) |
| J15 | 7 | 0x80 | noch offen |

Ablauf pro Messung:
1. Ein Byte mit genau **einem** gesetzten Bit an 0x70 schreiben und die Übertragung mit STOP abschließen.
2. Danach den VL53L0X unter **0x29** ansprechen.

Alle Sensoren behalten 0x29, XSHUT und Adressänderung sind nicht nötig. 0x00 trennt alle Kanäle.

4. **Ultraschall J5 bleibt als Reserve-Leiste** (TRIG GPIO 11, ECHO GPIO 16, über einen Pegelwandler). Er muss nicht bestückt bzw. angeschlossen werden.

**Bewegungssensor:** Statt des MPU-6050 sitzt ein **TDK ICM-42670-P** auf der Platine. Er liegt direkt am Hauptbus unter **0x68** (kein Konflikt mit 0x70). Er braucht einen eigenen Treiber, die MPU-6050-Register gelten nicht. Sein Interrupt INT1 liegt an GPIO 12.

## Komplette Pinbelegung ESP32-S3

| Funktion | GPIO |
|---|---|
| I²C SDA / SCL (IMU, TCA9548A) | 13 / 14 |
| IMU INT1 | 12 |
| Liniensensor LS1 … LS6 (alle ADC1) | 4, 5, 6, 7, 9, 10 |
| Akkuspannung BAT_ADC (ADC1_CH2) | 3 – U_Akku = U_ADC × 122 / 22 |
| Motor A Richtung / PWM | 48 / 47 (AIN2 wird per Inverter erzeugt) |
| Motor B Richtung / PWM | 41 / 42 (BIN2 wird per Inverter erzeugt) |
| Motortreiber STBY (aktiv HIGH, 10 kΩ nach GND) | 39 |
| Encoder M1 A / B | 38 / 21 |
| Encoder M2 A / B | 1 / 2 |
| Ultraschall TRIG / ECHO (Reserve J5) | 11 / 16 |
| RGB-LEDs WS2812B (8 Stück, vorne) | 8 |
| Benutzertaster (aktiv LOW) | 15 |
| USB vorhanden (LOW = USB gesteckt) | 40 |
| USB D− / D+ | 19 / 20 |
| UART0 TX / RX (an J3 Pin 3 / 5) | 43 / 44 |
| I²C-Multiplexer RESET (MUX_RSTn) | 37 |
| frei an J3 | 17, 18 |

## Bitte am fertigen Roboter prüfen („funktioniert es wie im Plan?“)

1. **I²C-Scan am Hauptbus:** 0x68 (IMU) und 0x70 (Multiplexer) müssen antworten. Danach je Kanal 0x01 … 0x80 setzen: Auf jedem belegten Kanal muss 0x29 antworten.
2. **Bus mit 400 kHz:** Mit der echten Kabellänge testen. Bei Fehlern zuerst mit 100 kHz gegenprüfen und die Flanken mit dem Oszilloskop ansehen.
3. **Messrate:** Continuous-Modus mit 20 ms pro Sensor, alle 8 messen gleichzeitig. Kanal wählen ≈ 0,05 ms, Status + Wert lesen ≈ 0,3 ms → 8 Sensoren reihum ≈ 3 ms. Erwartet: ≈ 50 Messungen pro Sekunde und Sensor. Nicht jede Millisekunde alle Kanäle pollen, sondern alle 5–20 ms reihum lesen.
4. **Akkuspannung:** BAT_ADC mit Dämpfung **12 dB** und eFuse-Kalibrierung messen und mit einem Multimeter am Testpunkt TP3 (VBAT_SW) vergleichen. Bei 2S und 3S prüfen, ob die Erkennung (> 9,0 V = 3S) stimmt.
5. **Motoren:**
   - Beim Start zuerst die Richtungen setzen und PWM = 0, erst danach STBY = 1.
   - Drehrichtung und Encoder-Vorzeichen am aufgebockten Roboter prüfen.
6. **USB:** Ob USB angesteckt ist, wird über GPIO 40 erkannt (LOW = angesteckt). Mit dieser Info den D+-Pull-up des S3 schalten (Self-Powered-Modus laut Espressif).
7. **Liniensensor:** Alle Kanäle liegen auf ADC1 und sind damit auch bei aktivem WLAN nutzbar. Schwarz und Weiß neu kalibrieren.
