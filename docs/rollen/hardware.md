# Rolle Hardware – Wissensdatei

Verantwortlich: Christopher. Diese Datei ist der Einstieg für jede KI, die Fragen an die Hardware beantwortet. Sie fasst den Stand zusammen und zeigt, **wo** die belastbaren Angaben stehen. Bei Widerspruch gelten die Dateien auf dem Branch `PCB`.

## Wo steht was (Branch `PCB`)

| Thema | Datei |
|---|---|
| Hauptplatine, Revisionen, Layout | `PCB/Tumbler_Mainboard/README.md` |
| Schaltplan erklärt, Stecker, Adressen, Tests | `PCB/Tumbler_Mainboard/README_Schaltplan.md` |
| Pinbelegung ESP32-S3, Hinweise für Firmware | `PCB/Tumbler_Mainboard/Hinweise_Software_Rev2.4.md` |
| Stückliste mit Werten und Footprints | `PCB/Tumbler_Mainboard/Stueckliste.csv` |
| Schaltplan (PDF / KiCad) | `PCB/Tumbler_Mainboard/Schaltplan.pdf`, `*.kicad_sch` |
| Platine (KiCad) | `PCB/Tumbler_Mainboard/Tumbler2_Redesign.kicad_pcb` |
| Steckerpositionen für das Gehäuse (mm, Ursprung links unten, Y nach oben) | `PCB/Tumbler_Mainboard/Mechanik/Gehauese_Bezugspunkte.csv` |
| Platinenumriss und Bohrungen | `PCB/Tumbler_Mainboard/Mechanik/Kontur_und_4_Bohrungen.dxf`, `Platine_ohne_Bauteile.step` |
| Liniensensor | `PCB/Liniensensor_Redesign/`, Belegung `PCB/Tumbler_Mainboard/Pinbelegung.csv` |

Datenblätter liegen beim Hardware-Menschen lokal (Ordner `Datenblaetter`), die wichtigsten Ausschnitte sind als Bilder im Schaltplan.

## Kurzfassung Stand Rev. 2.4 (12.11.2026, Prototyp, noch nicht gefertigt)

- **Controller:** ESP32-S3-WROOM-1-N8 (8 MB Flash, kein PSRAM). Programmieren über natives USB (GPIO 19/20), UART0 (GPIO 43/44) an J3.
- **Versorgung:** 2S-Li-Ion-Pack (6,0–8,4 V) → Schutz LTC4365 (UV 5,50 V / OV 8,75 V) → Schalter SW4 → `VBAT_SW`. Regler AP63203 → 3,3 V (2 A), AP63205 → 5 V (2 A). Fahrfreigabe TPS3700: Start ≈ 6,42 V, Stopp ≈ 6,0 V.
- **Laden:** USB-C, BQ25886, 8,4 V Ladeschluss, Ladestrom ≈ 0,25 A, Eingangsstrom ≤ 0,52 A.
- **I²C-Hauptbus:** SDA GPIO 13, SCL GPIO 14, 2,2 kΩ an 3,3 V, 400 kHz vorgesehen. IMU ICM-42670-P = 0x68, Multiplexer TCA9548A = 0x70.
- **ToF:** 8 × VL53L0X (GY-530) an TCA9548A-Kanälen 0–7, Lötpads J8–J15 (1 VIN +5 V, 2 GND, 3 SCL, 4 SDA), alle 0x29, **kein XSHUT**. MUX_RSTn = GPIO 37.
- **Motoren:** TB6612FNG an VBAT_SW. Motor A: DIR 48 / PWM 47, Motor B: DIR 41 / PWM 42, STBY GPIO 39 (aktiv HIGH, Pull-down). IN2 wird per Inverter erzeugt.
- **Encoder:** M1 A/B = GPIO 38/21, M2 A/B = GPIO 1/2 (5 V → 3,3 V über SN74LVC244).
- **Liniensensor:** LS1–LS6 = GPIO 4, 5, 6, 7, 9, 10 (alle ADC1), Stecker J2 (JST-GH 10).
- **Sonstiges:** RGB WS2812B ×8 an GPIO 8 (über Pegelwandler), Taster GPIO 15, USB erkannt GPIO 40 (LOW = gesteckt), Akkuspannung GPIO 3 (U_Akku = U_ADC × 122/22), Ultraschall-Reserve J5 (TRIG 11, ECHO 16).
- **Platine:** 4 Lagen (In1 = GND), 77 × 80,5 mm, 4 Bohrungen 3 mm. Vorne = Unterkante (LEDs, J2, J8). ESP32-Antenne ragt rechts über die Kante – davor kein Metall.

## Was die KI **nicht** entscheiden darf

Bauteilwerte, Pinbelegung, Steckerpositionen und Platinenmaße ändern sich nur durch Christopher. Fragen, die so eine Änderung brauchen (z. B. „Können wir den Stecker 5 mm verschieben?“), mit Einschätzung beantworten und `braucht-mensch` setzen.

## Offene Punkte (Stand Rev. 2.4)

- Einbauorte ToF-Kanäle 4–7 am Gehäuse.
- KiCad-DRC/ERC und Prototyp-Test stehen aus.
