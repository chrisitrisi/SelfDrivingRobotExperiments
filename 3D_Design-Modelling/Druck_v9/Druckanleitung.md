# Tumbler Chassis v9 – Druckanleitung (Bambu Lab P1S, Bambu PETG Basic)

**Status 26.11.2026: Chassis mit Version 2 erfolgreich gedruckt.** Version 1 (ohne Stützen, Standard-Erstschicht) hat sich in der ersten Schicht gelöst und ist nicht mehr im Repo.

Stand 19.11.2026. Grundlage: `3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.stl` (Revision v9.0, Commit 7c8b8c3).

## Dateien

| Datei | Inhalt |
|---|---|
| **`Tumbler_Chassis_v9_P1S_PETG-Basic_v2_Support.gcode.3mf`** | **Erfolgreich gedruckt (26.11.2026).** Bambu Lab P1S, 0,4-mm-Düse, Bambu PETG Basic, Textured PEI Plate, Stützen nur vom Druckbett. Direkt auf die microSD-Karte kopieren und am Drucker starten. |
| `Tumbler_Chassis_v9_P1S_platziert.3mf` | Modell, schon richtig auf der Platte platziert (45° gedreht). Nur nötig, wenn man selbst neu slicen will. |
| `Tumbler_Chassis_v9_Standoff+4.stl` | Dasselbe Teil in Original-Lage (Chassis-Koordinaten wie in der DMU). |
| `PrusaSlicer_Referenzprofil_Bambu_PETG.ini` | Erste Zeitabschätzung, nur zum Vergleich. |

## Version 2 (nach Fehldruck 19.11.): `Tumbler_Chassis_v9_P1S_PETG-Basic_v2_Support.gcode.3mf`

Beim ersten Versuch hat sich die erste Schicht in einer Kurve vom Bett gelöst und wurde mitgezogen (Haftung). Version 2 hat dafür:
- erste Schicht 0,25 mm hoch und 0,55 mm breit
- 30/40 mm/s (statt 50/105) und 300 mm/s² Beschleunigung
- Düse 255 °C, Bett 80 °C in der ersten Schicht, danach 75 °C, Lüfter in den ersten 3 Schichten aus
- Stützen nur vom Druckbett aus: Sie sitzen in den seitlichen Sensor-Pods, die unten offen sind, und lassen sich von unten herausziehen.

Druckzeit ca. 5 h 38 min, ca. 174 g. **Platte vorher gründlich mit Spülmittel und warmem Wasser waschen und nicht mehr auf die Druckfläche fassen** – Fingerfett ist die häufigste Ursache für PETG-Ablösung auf Textured PEI.

## Drucken von der SD-Karte

1. `Tumbler_Chassis_v9_P1S_PETG-Basic_v2_Support.gcode.3mf` in das Hauptverzeichnis der microSD-Karte kopieren und die Karte in den P1S stecken.
2. **Textured PEI Plate** einlegen. Vorher mit Spülmittel und Wasser oder IPA entfetten.
3. Bambu PETG Basic einlegen, im AMS oder als externe Spule. Am Drucker prüfen, dass der Slot auf **PETG** steht.
4. Am Display: Dateien → SD-Karte → Datei wählen.
   - „Bed Leveling“ **eingeschaltet** lassen.
   - Timelapse nach Wunsch.
   - Beim Filament-Mapping den Slot mit PETG wählen.
5. **Die ersten 2–3 Schichten beobachten.** Das Teil liegt diagonal und reicht bis knapp an alle vier Ränder. Die Ecken müssen sauber haften.

## Kennwerte

| | Wert |
|---|---|
| Druckzeit (Bambu Studio 2.9.1) | **5 h 38 min** (inkl. Aufheizen, Leveling, Ladelinie) |
| Filament | **174 g PETG** |
| Schichten | erste 0,25 mm, dann 0,20 mm, Höhe 29,5 mm |
| Einstellungen | 4 Wände, 5 oben / 4 unten, 20 % Gyroid, Stützen nur vom Druckbett, kein Brim, 255 °C, Bett 80/75 °C, erste Schicht 0,25 mm / 30–40 mm/s |

## Änderung gegenüber v9 (nur im STL)

**Die 4 Hauptplatinen-Standoffs sind 4 mm höher (Oberkante Z 25,5 → 29,5 mm).** Die Insert-Bohrung Ø 4,0 mm ist dadurch 10 mm tief statt 6 mm.

Grund: Zwischen Akku-Oberkante (Z 23,75) und Platinen-Unterseite waren nur 1,75 mm Luft. Auf der Unterseite der Hauptplatine Rev. 2.5 sitzen über dem Akkufach aber:
- D14 (SMB, ca. 2,3 mm hoch) und die 2S/3S-Brücken R87–R92
- 15 Testpunkte und die Pins von J3 (2 × 8) und SW4
- die angelöteten ToF-Kabel an J14

Jetzt sind es 5,75 mm.

**Achtung 3D-Team:** Die Änderung ist nur im STL gemacht. Der Fusion-Quellstand von v9 liegt nicht im Repo (das `.py` zu `v3_LiDar_V2_integrated` ist noch die alte v3-Fassung). Beim nächsten Export aus Fusion muss die Standoff-Höhe dort ebenfalls um 4 mm erhöht werden (in der DMU: `STANDOFF_Z = 29.5`), sonst ist die Änderung wieder weg.

## Platzierung auf der Platte (wichtig, falls jemand neu sliced)

Das Chassis (135,7 × 270,4 mm) passt beim P1S nur **45° diagonal**. In beiden Richtungen braucht es dann 250,5 mm von 256 mm. Zwei Stellen sind belegt:

- **Ladelinie des P1S:** vorne, bei Y ≈ 1,0–1,5 mm von X 18 bis 240, plus ein kurzes Stück bei X 240 bis Y 11. Das Chassis darf dort nicht liegen.
- **Düsenversatz:** Der P1S hat `extruder_offset = 0x2`. Bambu Studio verschiebt das Teil im G-Code um 2 mm nach vorne, die Ladelinie aber nicht.

Deshalb liegt das Modell in `…_platziert.3mf` auf Y 5,2–255,7 mm. Im G-Code bleiben damit **1,8 mm** zwischen Außenwand und Ladelinie, und kein Punkt liegt in der Sperrecke vorne links.

**Nicht einfach das STL in Bambu Studio importieren und mittig ablegen.** Dann läuft die Ladelinie unter die Außenwand. Beim Neu-Slicen in Bambu Studio die `…_platziert.3mf` laden, Lage nicht verändern und nicht „Anordnen“ drücken.

## Hinweis „floating cantilever“

Bambu Studio warnt vor frei auskragenden Stellen. Das sind die Decken der 8 Sensorkammern (Brücken bis ca. 22–25 mm) und einige kleine Überhänge an den Pods. Stützen sind dort bewusst aus: In den Sensorkammern wären sie kaum zu entfernen, und Reste würden den Sensor blockieren. Leichter Durchhang an den Kammerdecken ist unkritisch. Nach dem Druck prüfen und ggf. entgraten.

## Nach dem Druck

- 4 × **M3-Gewindeeinsätze** (Heat-Set, für Ø 4,0 mm Bohrung, z. B. M3 × 5,7) mit dem Lötkolben (ca. 220 °C bei PETG) bündig in die Standoffs setzen. Die Platine wird mit 4 × M3 × 8 verschraubt.
- 16 × **M2 × 6** für die 8 ToF-Sensoren (Ø 2,0 mm Sacklöcher, direkt ins PETG schrauben, nicht überdrehen).
- Liniensensor (76 × 32 mm, M3-Raster 68 × 24 mm) – passt zur Halterung.
- Platine probehalber einlegen: Unterseite (D14, Brücken, Testpunkte, J3-Pins) darf den Akku nicht berühren. Akku zusätzlich mit Kaptonband oder einer dünnen Isolierplatte abdecken.

## Offene Punkte für das 3D-Team (nicht im STL geändert)

1. **Platinen-Modell in der DMU veraltet.** Dort sind TB67H450 (2×), LSM6DSV, J2 als 2,54-mm-Stiftleiste und J3 als „LiDAR-Bus“ modelliert.
   - Rev. 2.5 hat stattdessen: 1 × TB6612FNG, ICM-42670-P, J2 = JST GH 10-polig liegend an der Vorderkante, J3 = UART-Leiste, ToF-Sensoren über Lötpads J8–J15.
   - J1 (Akku, JST XH) sitzt bei Chassis ≈ (38,7 / −108,9).
   - Die Freiraumprüfung der Stecker ist damit nicht aussagekräftig. Die Bohrungen H1–H4 (Raster 65 × 64 mm) stimmen.
2. **Akku:** Modelliert ist ein 2S-Pack 72 × 39,5 × 19,5 mm mit XT30 und 3S-Balancer. Die vorhandenen Akkus haben JST-XH-Stecker. Bitte echte Maße messen.
3. **3S:** Die Platine kann ab Rev. 2.5 auch mit 3S fahren. Ein 3S-Pack passt aber nicht ins 78 × 43,5 × 21,5 mm Fach.
4. Das Teil braucht mindestens ein 256 × 256 mm Bett (nur diagonal) bzw. 300 × 300 mm gerade.
