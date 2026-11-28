# Hauptplatine Rev. 2.5c bei JLCPCB bestellen

## Dateien für den Upload

Für das Fahrzeug ist **3S** der Standard. Als PCB-Datei in beiden Varianten `Gerber_JLC_Hauptplatine.zip` hochladen. Das ZIP enthält vier Kupferlagen, Kontur, Lötstopp, Paste, Siebdruck sowie getrennte PTH- und NPTH-Bohrdaten. Platinenaufbau FR4, 1,6 mm, 1 oz Außen- und Innenkupfer.

| Bestückung | BOM | CPL | SMD oben / unten |
|---|---|---|---:|
| **Standard PCBA beidseitig · 3S** | [BOM_JLC_beidseitig.csv](BOM_JLC_beidseitig.csv) | [CPL_JLC_beidseitig.csv](CPL_JLC_beidseitig.csv) | 168 / 15 |
| Standard PCBA beidseitig · 2S | [BOM_JLC_2S_beidseitig.csv](BOM_JLC_2S_beidseitig.csv) | [CPL_JLC_2S_beidseitig.csv](CPL_JLC_2S_beidseitig.csv) | 168 / 20 |
| Optional nur Oberseite · Standard PCBA | [BOM_JLC.csv](BOM_JLC.csv) | [CPL_JLC.csv](CPL_JLC.csv) | 168 / 0 |

Bei beidseitiger Bestellung J1, J3, J5 und SW4 anhand von [Selbst_bestuecken.csv](Selbst_bestuecken.csv) separat beschaffen und nach dem Reflow löten. Bei einseitiger Bestellung zusätzlich die zur Variante gehörenden Teile der Unterseite löten, einschließlich R90/R91. Für 2S-Laden wird dort auch C30 benötigt.

JLC listet U3, U5, U10 und die acht RGB-LEDs D6–D13 als **Standard Only**. Das gilt auch für den einseitigen Auftrag. Den [Liniensensor](../../Liniensensor_Redesign/Fertigung/README.md) als eigenen zweilagigen Economic-Auftrag anlegen. Stückpreise, Rüstkosten und Bestand ergeben sich aus Stückzahl und Warenkorb.

[U3 · ESP32-S3](https://jlcpcb.com/partdetail/ESP32-S3-WROOM-1-N8/C2913198) · [U5 · IMU](https://jlcpcb.com/partdetail/TDKInvenSense-ICM_42670P/C3288646) · [U10 · USB-C](https://jlcpcb.com/partdetail/TexasInstruments-TUSB320LAIRWBR/C132554) · [D6–D13 · WS2812B-2020-V6](https://jlcpcb.com/partdetail/Worldsemi-LED/C52917434)

## Kontrolle in der Bestückungsvorschau

- Grundvariante 3S hat R87, R88, R89, R92 und D14 frei (D14 hängt nur an R92). In der separaten 2S-Variante sind alle fünf bestückt. R90 und R91 sind in beiden Varianten vorhanden.
- J4 an den 16 Kontakten, den Führungsbohrungen und den vier Haltelaschen ausrichten. Bei J2, J6 und J7 Pin 1, Steckrichtung und Laschen prüfen. Die CPL enthält bereits die Korrektur vom Footprint-Ursprung auf die Mitte der gezeichneten Gehäusekontur. Die Gurt- bzw. Greifpunkte im JLC-Modell können davon abweichen.
- Polung von C17 und den Dioden sowie Pin 1 von U3, U5, U10 und U12 prüfen. Die [Rotationsliste](Rotation_pruefen.txt) und die Bestückungspläne für [oben](Bestueckungsplan_oben.pdf) und [unten](Bestueckungsplan_unten.pdf) zeigen die Orientierung. Die Unterseitenzeichnung ist gespiegelt und wird von unten betrachtet.
- Bei J4 die Abstände von ca. 0,150–0,185 mm zwischen SMD-Pads und Führungsbohrungen mit JLC abgleichen. Die lokale KiCad-Regel behandelt die Pads dieses Steckers. Für die Wärmevias in U3.41 und U12.25 mit JLC das Via-Verfahren und die Pastenöffnungen abstimmen.

## Mechanik und Inbetriebnahme

Die [bestückte 3S-Baugruppe als STEP](../Mechanik/Mainboard_3S_Rev25c_STEP.zip) enthält die vier THT-Teile und die SMD-Teile; D14 ist darin noch enthalten, in der 3S-Bestückung bleibt er frei (183 SMD-Positionen). U10 wird durch das vereinfachte Projektmodell dargestellt. Kabel, Steckergegenstücke und Akku bei der Passprobe ergänzen. C69.1 hat im Nennmaß 1,30 mm Abstand zur H4-Stütze mit 5,5 mm Radius.

Die Baugruppe hat denselben Ursprung wie `Platine_ohne_Bauteile.step` und `Gehauese_Bezugspunkte.csv`. Beim STEP-Export in KiCad den Ursprung `--user-origin 113.792x145.288mm` verwenden. H4 liegt damit bei X 6,013 und Y 9,928 mm. Die Außenkontur misst 76,962 × 80,518 mm. Mit Steckern und Bauteilen reicht das Modell bis X 82,958 mm und in Z von −2,235 bis +11,595 mm.

Vor dem ersten Anschluss die Polarität an J1 und die vier Brücken kontrollieren. 3S extern laden. Für 2S die Ladefreigabe mit Pack-NTC, Ladeende und Verhalten in RUN/OFF prüfen. Die Prüfungen für den ersten Fahrversuch einschließlich VM am Motortreiber sind im [Schaltplanbegleittext](../README_Schaltplan.md) beschrieben.

## Nach einer Änderung

Mit KiCad 10 Gerber und Bohrdaten, Schaltplan-PDF und Bestückungspläne aus demselben Stand neu exportieren. `python export_bestueckung.py` im Hauptboard-Verzeichnis erzeugt aus Schaltplan und Layout beide BOM-/CPL-Paare sowie die Handbestückungsliste. Das Skript verwendet `kicad-cli` vom PATH oder den Pfad in `KICAD_CLI`. Die Standardvariante und die KiCad-Variante `2S` werden getrennt ausgewertet.
