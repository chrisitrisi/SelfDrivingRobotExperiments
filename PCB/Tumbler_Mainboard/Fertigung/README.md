# Fertigungsdaten Hauptplatine Rev. 2.5a (JLCPCB)

Erzeugt am 26.11.2026 mit KiCad 10.0.7 aus diesem Stand. Nach jeder Änderung an der Platine neu exportieren.

| Datei | Zweck |
|---|---|
| `Gerber_JLC_Hauptplatine.zip` | Gerber (4 Lagen) und Bohrdaten zum Hochladen |
| `BOM_JLC.csv` / `CPL_JLC.csv` | Stückliste und Bestückungspositionen, **Variante 2S** (R87/R88/R89/R92 = 0 Ω bestückt) |
| `Selbst_bestuecken.csv` | THT-Teile, die ihr selbst lötet (J1, J3, J5, SW4) |
| `Positionen_KiCad.csv` | KiCad-Originalpositionen |
| `Ansicht_oben.png` / `Ansicht_unten.png` | 3D-Ansichten zur Kontrolle |

**Bestelloptionen:** 4 Lagen, FR4, 1,6 mm, Außenlagen 1 oz, **Innenlagen 1 oz** (nicht 0,5 oz: Motor- und Akkuleitungen laufen teilweise auf In2.Cu), Lötstopp grün, Vias abgedeckt (tented). Bestückung beidseitig (oben 167, unten 18 Positionen).

**3S-Variante:** R87, R88, R89, R92 aus BOM und CPL streichen (bzw. nachträglich auslöten, R87 zuerst).

**Vor dem Bezahlen in der JLC-Vorschau prüfen:**
- Pin 1 und Drehung aller ICs und gepolten Teile (Rotationen aus KiCad können bei JLC abweichen).
- USB-C J4: Der Hersteller-Footprint hat 0,15–0,18 mm zwischen Pads und Führungslöchern (Projektregel 0,2 mm). DFM-Ergebnis von JLC abwarten.
- Wärme-Vias in den Thermalpads von U3 (ESP32-S3) und U12 (BQ25886) sind gewollt.
- LCSC-Teilenummern fehlen bei vielen Positionen; beim Matching Wert, Gehäuse und Spannungsfestigkeit aus `../Stueckliste.csv` übernehmen.
