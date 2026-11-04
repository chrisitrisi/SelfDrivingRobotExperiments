# Tumbler Liniensensor - Layout R2

Das gesamte ZIP entpacken und **Liniensensor.kicad_pro** in KiCad 9 oder neuer öffnen.
Alle Unterordner zusammenlassen. Schaltung R1 blieb elektrisch unverändert.

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
