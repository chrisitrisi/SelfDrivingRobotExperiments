# Fertigungsdaten Hauptplatine Rev. 2.5b (JLCPCB)

Erzeugt am 28.11.2026 mit KiCad 10.0.7 (`_review/export.ps1` + `_review/jlc.py`). Nach jeder Änderung an der Platine neu exportieren.
Alle 188 SMD-Positionen haben eine LCSC-Nummer (Feld `LCSC PN` in Schaltplan und Platine, Lagerstand bei JLC am 28.11.2026 geprüft, Basic-Teile bevorzugt).

| Datei | Zweck |
|---|---|
| `Gerber_JLC_Hauptplatine.zip` | Gerber (4 Lagen) und Bohrdaten zum Hochladen |
| `BOM_JLC.csv` / `CPL_JLC.csv` | **Empfohlen, günstig:** nur Oberseite (168 Teile) → *Economic PCBA* |
| `BOM_JLC_beidseitig.csv` / `CPL_JLC_beidseitig.csv` | Alternativ: beide Seiten (188 Teile) → *Standard PCBA*, deutlich teurer |
| `Selbst_bestuecken.csv` | THT (J1, J3, J5, SW4) und – bei Economic – die 20 Teile der Unterseite, mit LCSC-Nummer zum Mitbestellen |
| `Rotation_pruefen.txt` | Teile, deren Drehung/Pin 1 in der JLC-Vorschau kontrolliert werden muss |
| `Bestueckungsplan_oben.pdf` / `_unten.pdf` | Bestückungspläne mit allen Referenzen (Fab-Lage) |
| `BOM_KiCad.csv`, `Positionen_KiCad.csv` | KiCad-Originale |
| `Ansicht_oben.png` / `Ansicht_unten.png` | 3D-Ansichten |

**Leiterplatte:** 4 Lagen, FR4, 1,6 mm, Außenlagen 1 oz, **Innenlagen 1 oz** (nicht 0,5 oz: Motor- und Akkuleitungen laufen teilweise auf In2.Cu), Lötstopp grün, Vias abgedeckt (tented).

**Unterseite (bei Economic selbst löten):** R79–R86, R90, R91, C69–C72, C30 (BTST-Kondensator des Laders – ohne ihn lädt U12 nicht), D14 und die 2S/3S-Brücken R87, R88, R89, R92. Alles 0603/0402/1206 bzw. SMB, gut von Hand lötbar.
**2S (Auslieferung):** R87/R88/R89/R92 = 0 Ω bestücken. **3S:** weglassen (bzw. R87 zuerst auslöten). In der beidseitigen Variante sind die Brücken für 2S enthalten.

**Kosten (Richtwert JLC-Teilepreise 28.11.2026):** Teile ≈ 33 $ pro Hauptplatine (davon ESP32 4,9 $, LTC4365 4,9 $, XEL4030 2,9 $). 30 Basic- und 39 Extended-Positionen; JLC berechnet pro Extended-Teilenummer einmalig ca. 3 $ Rüstgebühr pro Auftrag.

**Vor dem Bezahlen in der JLC-Vorschau prüfen:**
- Rotation/Pin 1 der Teile aus `Rotation_pruefen.txt` (Standard-Korrekturen für SOT-23, SOIC, TSSOP, SSOP, QFN, SMB und Elko sind schon eingerechnet).
- USB-C J4: Hersteller-Footprint hat 0,15 mm zwischen Pads und Führungslöchern (Projektregel `.kicad_dru`). DFM-Ergebnis von JLC abwarten.
- Wärme-Vias in den Thermalpads von U3 (ESP32-S3) und U12 (BQ25886) sind gewollt.
