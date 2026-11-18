# Rolle Software – Wissensdatei

Verantwortlich: Softwareentwicklung. Einstieg für jede KI, die Fragen an die Software beantwortet. **Bitte von der Software-Rolle aktuell halten.**

## Wo steht was

| Thema | Ort |
|---|---|
| ESP-IDF-Projekt, ToF-Versuch (4 Sensoren mit XSHUT) | Branch `code`, `main/main.cpp` |
| Erster ToF-Versuch | Branch `Main_code` |
| Tests | Branch `Test` |
| Offene Firmware-Anpassung an Hauptplatine Rev. 2.4 (8 ToF über Multiplexer) | Issue #3 |

## Stand

- Framework: ESP-IDF (C++), VL53L0X-Komponente in `components/vl53l0x`.
- Der vorhandene Code ist noch für den ESP32-WROOM-32E geschrieben (SDA 21 / SCL 22). Die neue Platine hat einen ESP32-S3 – siehe `docs/rollen/hardware.md` und Issue #3.

## Was die KI **nicht** entscheiden darf

Architektur, Regelalgorithmen und Pin-Wünsche an die Hardware werden von der Software-Rolle entschieden. Bei Bedarf `braucht-mensch` setzen.

## Offene Punkte

- _(von der Software-Rolle ergänzen)_
