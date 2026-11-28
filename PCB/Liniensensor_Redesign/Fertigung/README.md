# Fertigungsdaten Liniensensor R3.1 (JLCPCB)

Erzeugt am 28.11.2026 mit KiCad 10.0.7. ERC 0, DRC 0 (inkl. Schaltplan-Parität).

- `Gerber_JLC_Liniensensor.zip`: Gerber (2 Lagen) und Bohrdaten zum Hochladen.
- `BOM_JLC.csv` / `CPL_JLC.csv`: 31 SMD-Teile, alle oben, alle mit LCSC-Nummer (7 Basic, 2 Extended; Teile ≈ 1 $ pro Platine) → Economic PCBA.
- `Selbst_bestuecken.csv`: die sechs CNY70 (U1–U6, unten, LCSC C145423) selbst einlöten, mit 0,5-mm-Abstandslehre (optische Fläche 2 mm über Boden).
- Bestelloptionen: 2 Lagen, FR4, 1,6 mm, 1 oz.
- Q1/Q2: **Nexperia BCX56-16,115 (C100026)** – Pin 1 = Emitter, Pin 2 = Kollektor, Pin 3 = Basis, passend zum Footprint. Keine anderen BCX56-Klone wählen, ohne die Pinbelegung zu prüfen.
- `Rotation_pruefen.txt`: SOT-89 und JST-GH in der JLC-Vorschau kontrollieren.
