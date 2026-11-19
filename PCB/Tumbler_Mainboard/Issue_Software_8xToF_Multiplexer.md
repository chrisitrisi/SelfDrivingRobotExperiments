## Worum geht es

Die Hauptplatine wird auf **Rev. 2.4** umgestellt: Es kommen **8 × VL53L0X (GY-530)** an einen **I²C-Multiplexer TCA9548A**. Dadurch ändert sich die Ansteuerung gegenüber dem aktuellen Stand im Branch `code` (`main/main.cpp`, 4 Sensoren mit XSHUT und Adresswechsel).

**Kurz:** Kein XSHUT mehr, keine Adressänderung. Alle 8 Sensoren bleiben auf **0x29**. Vor jedem Zugriff wird über den Multiplexer der Kanal gewählt.

## Hardware (Rev. 2.4)

| | |
|---|---|
| Controller | ESP32-S3-WROOM-1-N8 (nicht mehr der ESP32-WROOM-32E) |
| I²C SDA / SCL | **GPIO 13 / GPIO 14**, externe Pull-ups 2,2 kΩ an 3,3 V |
| Multiplexer | TCA9548A, Adresse **0x70** |
| MUX_RSTn | **GPIO 37** (aktiv LOW; 10 kΩ Pull-up auf der Platine, Multiplexer läuft also auch, solange der Pin nicht gesetzt ist) |
| IMU | ICM-42670-P direkt am Hauptbus, **0x68** (kein Konflikt mit 0x70) |
| Sensor-Lötpads | 1 VIN (+5 V), 2 GND, 3 SCL, 4 SDA. XSHUT und GPIO1 des GY-530 sind **nicht** angeschlossen. |

| Kanal | Steuerbyte an 0x70 | Lötpads | Einbauort |
|---:|---:|---|---|
| 0 | 0x01 | J8 | vorne |
| 1 | 0x02 | J9 | rechts vorne |
| 2 | 0x04 | J10 | rechts Mitte |
| 3 | 0x08 | J11 | rechts hinten |
| 4 | 0x10 | J12 | noch offen (Gehäuse) |
| 5 | 0x20 | J13 | noch offen |
| 6 | 0x40 | J14 | noch offen (Platinenhinterkante) |
| 7 | 0x80 | J15 | noch offen |

Jeder Kanal hat eigene 2,2-kΩ-Pull-ups. Nach dem Einschalten und nach einem Reset sind alle Kanäle getrennt.

## Was in der Firmware geändert werden muss

1. **Ziel auf ESP32-S3 umstellen:** `idf.py set-target esp32s3`. SDA/SCL von 21/22 auf **13/14** ändern.
2. **XSHUT-Logik entfernen:** `XSHUT_PINS[]`, `ADDRESSES[]`, das nacheinander Aufwecken und `setAddress()` fallen weg.
3. **`NUM_SENSORS = 8`.**
4. **Kanalwahl einbauen.** Vor *jedem* Zugriff auf Sensor *i* ein Byte `1 << i` an 0x70 schreiben (eine eigene, mit STOP abgeschlossene Übertragung):
   ```cpp
   static const uint8_t MUX_ADDR = 0x70;
   static esp_err_t muxSelect(uint8_t ch) {
     uint8_t mask = (uint8_t)(1u << ch);
     return i2c_master_write_to_device(I2C_PORT, MUX_ADDR, &mask, 1, pdMS_TO_TICKS(5));
   }
   ```
   `0x00` trennt alle Kanäle. Die IMU (0x68) ist unabhängig vom Kanal immer erreichbar.
5. **Init:**
   ```cpp
   for (int i = 0; i < NUM_SENSORS; i++) {
     muxSelect(i);
     sensors[i].setPort(I2C_PORT);
     sensors[i].setTimeout(500);
     sensorOk[i] = sensors[i].init();      // Adresse bleibt 0x29
     if (sensorOk[i]) {
       sensors[i].setMeasurementTimingBudget(20000);
       sensors[i].startContinuous();
     }
   }
   ```
6. **Auslesen:** wie bisher im Continuous-Modus, aber pro Sensor erst den Kanal wählen:
   ```cpp
   muxSelect(i);
   if (dataReady(sensors[i])) lastDistance[i] = sensors[i].readRangeContinuousMillimeters();
   ```
   Bitte **nicht mehr jede Millisekunde alle Sensoren abfragen**, sonst ist der Bus dauerbelegt. Besser: alle 5 ms reihum, oder fest alle 20 ms einmal alle 8 lesen.
7. **MUX_RSTn (GPIO 37)** beim Start als Ausgang HIGH setzen. Bei I²C-Timeouts: kurz LOW (≥ 1 µs), wieder HIGH, Kanal neu wählen, betroffenen Sensor neu initialisieren.
8. **Der alte Code ist nicht 1:1 übertragbar:** Andere GPIOs und kein XSHUT, siehe `Hinweise_Software_Rev2.4.md` im Ordner `PCB/Tumbler_Mainboard` (komplette Pinbelegung des ESP32-S3).

## Geschwindigkeit (Abschätzung bei 400 kHz)

| Schritt | Dauer |
|---|---|
| Kanal wählen (1 Byte an 0x70) | ≈ 0,05 ms |
| Status lesen + Messwert lesen + quittieren | ≈ 0,3 ms |
| **8 Sensoren reihum** | **≈ 3 ms** |

Die Sensoren messen trotz Multiplexer **gleichzeitig**. Der Multiplexer schaltet nur die Verbindung zum ESP um. Bei 20 ms Messzeit liefert jeder Sensor weiterhin **≈ 50 Werte/s**, genau wie jetzt mit 4 Sensoren. Die Busauslastung liegt grob bei 15–30 %.

## Bitte prüfen

- [ ] I²C-Scan am Hauptbus: 0x68 und 0x70 antworten.
- [ ] Je Kanal (0x01 … 0x80): 0x29 antwortet.
- [ ] Messrate pro Sensor ≈ 50/s mit allen 8 Sensoren.
- [ ] Mit den echten Kabellängen bei 400 kHz testen, bei Fehlern mit 100 kHz gegenprüfen.
- [ ] Sensoren mit überlappendem Sichtfeld (25°) auf gegenseitige Störung prüfen, ggf. Messungen zeitlich versetzt starten.
- [ ] Reset über GPIO 37 testen (Sensor abziehen, Fehler provozieren, Wiederanlauf).
