# Tumbler Liniensensor - Layout R3 (2S und 3S)

Das gesamte ZIP entpacken und **Liniensensor.kicad_pro** in KiCad 9 oder neuer öffnen.
Alle Unterordner zusammenlassen.

**R3.1 (26.11.2026): Pinbelegung Q1/Q2 korrigiert.** Der BCX56 hat im SOT-89 **Pin 1 = Emitter, 2 = Kollektor, 3 = Basis** (NXP- und Diodes-Datenblatt). Das KiCad-Standardsymbol `Transistor_BJT:BCX56` ist fälschlich B-C-E belegt, dadurch lagen Basis und Emitter vertauscht auf dem Footprint (Sensor wäre ohne LED-Strom gewesen). Jetzt eigenes Symbol `Tumbler_Sensor:BCX56_ECB`; Q1/Q2 neu angeschlossen (Pad 1 → 47-Ω-Emitterwiderstand R1/R9, Pad 3 → Basisteiler). DRC 0, ERC nur die zwei bekannten Label-Hinweise, Schaltplan-Parität ohne Netzabweichung. Gerber/Bohrdaten neu.

**R3 (26.11.2026):** Läuft an 2S **und** 3S (VBAT_SW 6,0–12,6 V, Spitzen 13,5 V) ohne Umbau. Q1/Q2 jetzt BCX56-16 (SOT-89) statt BC817-40, Basisteiler R2/R3/R7/R8 470 Ω statt 1 kΩ. Details und Rechnung: `Hinweise.md`. Gerber, Bohrdaten, Ansichten und `Mechanik/Liniensensor.step` sind auf R3 aktualisiert (KiCad 10).

Noch nicht nachgezogen: `Montage_und_Layout.pdf` nennt als Versorgung noch „2S“ (Mechanik/Lochbild darin unverändert gültig). Der Unterordner `Liniensensor_Redesign/` ist eine ältere Kopie (Schaltung R1, BC817) und nicht der aktuelle Stand.

- `Liniensensor.kicad_pcb`: vollständig geroutete Sensorplatine, 76 × 32 mm.
- `Liniensensor.kicad_sch` / `Liniensensor.pdf`: Schaltplan.
- `Montage_und_Layout.pdf`: Lochbild, Höhenkette, Vorlauf zur Radachse, Montage und Erprobung.
- `Mechanik/`: bestückte PCB als STEP; Halter und Distanzscheiben als STL; editierbarer OpenSCAD-Entwurf.
- `Fertigung/`: Gerber, PTH-/NPTH-Bohrdateien und Bohrbericht für diesen Prototyp.
- `Stueckliste.csv` und `Hinweise.md`: Bauteile, elektrische Auslegung und Pinbelegung.
- `Ansichten/`: tatsächliche CAD-Ansichten.
- `Pruefung.txt`, `Layoutpruefung.json`, `ERC.json`, `DRC.json`: Prüfstand.
- `symbols/`, `footprints/`, `3dmodels/`, lokale Bibliothekstabellen: mitgelieferte Bibliotheken.
- `Lizenzen/`: KiCad-Bibliothekslizenzen und Quellen.

## Mechanische Startwerte

Optische Fläche 2 mm über dem Boden, Sensoren mit 0,5 mm Sitzabstand zur PCB löten.
Daraus nominal: PCB-Unterseite 8,5 mm und Oberseite 10,1 mm über Boden.
Der Halter liegt oben bei 19,1 mm; diese Anlagefläche muss im neuen Gehäuse vorgesehen werden.
Vorlauf als Start: 20 mm vor der vordersten Reifenkante, also L = Raddurchmesser/2 + 20 mm vor der Radachse.
20 mm Längsverstellung im Halter. Reifenfreiheit, Linienbreite und Gehäusepassung vor Bestellung prüfen.
Der Halter ist ein universeller Adapter, kein am vorhandenen Chassis vermessener Ersatz.

## Fertigung

FR4, 2 Lagen, 1,6 mm, 35 µm Kupfer, Lötstopp beidseitig. CNY70 unten, alle SMD-Bauteile oben.
Nicht versehentlich nur die Platine aus dem ZIP herauskopieren: Bibliotheken und 3D-Modelle gehören dazu.
Nach eigenen Änderungen Massefläche neu füllen und ERC/DRC ausführen; Gerber anschließend neu exportieren.
Elektrische Regelprüfung ohne Befund, keine Freigabe eines am Roboter erprobten Serienstands.
