# 2-Lagen-Versuch der Hauptplatine (Branch `pcb/2-lagen-versuch`)

Stand 26.11.2026. Ausgangspunkt: Rev. 2.5 (4 Lagen, Commit 7b104d0 auf `PCB`). **Versuch, nicht fertigungsreif.**

Ziel: prüfen, ob die Platine mit 2 statt 4 Lagen (günstiger) machbar ist.

## Ergebnis

| | |
|---|---|
| ERC | 0 Fehler, 0 Warnungen |
| Schaltplan-Parität | 0 |
| Offene Verbindungen | **57** (33 Signale, 24 GND-Inseln) |
| Abstandsfehler | 1 (dazu die bekannten 8 × J4-NPTH, 7 Courtyards) |
| Bericht | `Pruefung/DRC_2Lagen_Versuch.json`, `Pruefung/ERC_2Lagen_Versuch.json` |

Offene Signale: /LiDAR x8/SCL, /LiDAR x8/SDA2, /MCU/BTN, /MCU/DIR_A, /MCU/DN, /MCU/ECHO, /MCU/ENCA_A, /MCU/ENCA_B, /MCU/ENCB_A, /MCU/ENCB_B, /MCU/INT1, /MCU/LS1, /MCU/LS2, /MCU/LS3, /MCU/LS4, /MCU/PWMA, /MCU/TRIG, /Peripherals/M1_A_RAW, /Peripherals/M1_B_RAW, /Peripherals/M2_N, /RGB LEDs/RGB, /USB-C / 2S charger/REGN, /USB-C / 2S charger/STATn, MOTOR_STBY, MUX_RSTn, VBAT_SW

**Fazit:** Mit automatischem Routing allein nicht fertig zu bekommen. Engstelle ist der Bereich links und unter dem ESP32-S3 (fast alle Signale laufen dort zusammen) sowie die GND-Versorgung ohne durchgehende Masselage. Ohne GND-Lage werden außerdem USB (D+/D−), die Schaltregler und die Motorströme elektrisch schlechter. Bei Kleinserien sparen 2 statt 4 Lagen erfahrungsgemäß nur wenige Euro (Preise im Rechner des Herstellers prüfen).

## Was gemacht wurde

1. In2-Bahnen (1,75 m, 68 Netze) und GND-Lage In1 entfernt, Lagenanzahl 2. Antennen-Sperrflächen auf F/B beschränkt.
2. **ESP32-Pinbelegung neu verteilt** (Schaltplan `mcu.kicad_sch`, Netzliste geprüft: jedes Netz verbindet dieselben Bauteile wie vorher, nur der ESP-Pin ist anders). Ziel: jedes Signal an die Modulkante, von der seine Quelle kommt.
3. Alle Bahnen der 31 betroffenen Netze gelöscht, alles mit eigenem Raster-Router (A*, F/B, Vias) neu verlegt.
4. GND-Inseln mit 47 Verbindungs-Vias und 123 Stitching-Vias (Raster 4 mm) verbunden.
5. Rip-up-and-Reroute ausprobiert: verschlechtert das Ergebnis (64 → 225 offen) und wurde verworfen.

## Neue ESP32-Pinbelegung (nur in diesem Branch!)

Regeln aus den Espressif-Datenblättern (ESP32-S3-WROOM-1 v1.8, ESP32-S3 v2.2):
- GPIO35/36/37 sind beim **N8 (ohne PSRAM)** frei, gesperrt nur bei Octal-PSRAM-Modulen (R8/R16V).
- GPIO47/48 arbeiten beim N8 mit 3,3 V (1,8 V nur bei R16V).
- Strapping-Pins GPIO0 (Pull-up), GPIO45 (Pull-down, VDD_SPI) und GPIO46 (Pull-down) bleiben unbenutzt bzw. unverändert. GPIO3 (JTAG-Quelle) wirkt nur bei gebrannter eFuse.
- ADC1 = GPIO1–10 (mit WLAN nutzbar), ADC2 nicht mit WLAN → Liniensensoren und Akkumessung auf GPIO1–10.
- **GPIO39 (MTCK) hat nach dem Reset einen internen Pull-up.** Deshalb liegt MOTOR_STBY jetzt auf GPIO7. Das ist auch für die 4-Lagen-Platine eine Verbesserung.
- GPIO18 hat beim Einschalten einen HIGH-Puls → nicht für Motor-Ausgänge.
- Fest: USB GPIO19/20, UART0 GPIO43/44, EN, GPIO0.

| Signal | alt (Rev. 2.5) | neu | Modulpin |
|---|---|---|---|
| LS6 | GPIO10 | **GPIO1** | 39 |
| LS5 | GPIO9 | **GPIO2** | 38 |
| LS2 | GPIO5 | **GPIO3** | 15 |
| LS4 | GPIO7 | **GPIO4** | 4 |
| PWMA | GPIO47 | **GPIO5** | 5 |
| DIR_A | GPIO48 | **GPIO6** | 6 |
| MOTOR_STBY | GPIO39 | **GPIO7** | 7 |
| BAT_ADC | GPIO3 | **GPIO8** | 12 |
| LS1 | GPIO4 | **GPIO9** | 17 |
| LS3 | GPIO6 | **GPIO10** | 18 |
| ENCB_B | GPIO1 | **GPIO11** | 19 |
| ENCA_B | GPIO2 | **GPIO12** | 20 |
| INT1 | GPIO12 | **GPIO13** | 21 |
| ECHO | GPIO16 | **GPIO14** | 22 |
| DIR_B | GPIO41 | **GPIO15** | 8 |
| PWMB | GPIO42 | **GPIO16** | 9 |
| ENCB_A | GPIO38 | **GPIO17** | 10 |
| ENCA_A | GPIO21 | **GPIO18** | 11 |
| TRIG | GPIO11 | **GPIO21** | 23 |
| MUX_RSTn | GPIO37 | **GPIO35** | 28 |
| RGB | GPIO8 | **GPIO36** | 29 |
| USB_PRESENTn | GPIO40 | **GPIO37** | 30 |
| BTN | GPIO15 | **GPIO38** | 31 |
| SPARE2 | GPIO18 | **GPIO39** | 32 |
| SPARE1 | GPIO17 | **GPIO40** | 33 |
| SDA | GPIO13 | **GPIO47** | 24 |
| SCL | GPIO14 | **GPIO48** | 25 |

GPIO41 und GPIO42 sind jetzt frei (No-Connect). IO17/IO18 an J3 heißen jetzt SPARE1/SPARE2.

**Für die Software:** Diese Pinbelegung gilt nur, wenn die 2-Lagen-Platine wirklich gebaut wird. Die gefertigte/gepushte Rev. 2.5 behält die Belegung aus `Hinweise_Software_Rev2.5.md`.

## Wenn man weitermachen will

- Von Hand in KiCad mit dem interaktiven Router (Schieben/Ausweichen) die 33 offenen Signale legen, beginnend am ESP32.
- 3,3 V und VBAT_SW als Flächen statt Bahnen ausführen, die blockieren den Korridor am meisten.
- Die Unterseite unter dem ESP32-Modul gezielt für den Pin-Fan-out nutzen.
- GND-Inseln: an den Pads mit kurzen Bahnen zur nächsten GND-Via anbinden.
- Platine eventuell etwas größer machen (Chassis prüfen).

## Werkzeuge

`Werkzeuge_2Lagen/` enthält die verwendeten Skripte (Python mit KiCad-10-pcbnew): `assign.py` (Pinzuordnung, Hungarian), `rebuild_mcu.py` (Schaltplan-Umbau), `prep_swap.py` (2 Lagen + neue Pads), `route2L.py`/`rt.py` (Router), `stitch.py` (GND-Vias), `ripup.py`/`loop.sh` (Rip-up, verworfen), `congest.py` (Engstellen-Analyse). Die Pfade in den Skripten zeigen noch auf einen temporären Arbeitsordner und müssen vor erneutem Gebrauch angepasst werden.
