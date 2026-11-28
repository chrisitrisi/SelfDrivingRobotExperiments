# Tumbler – Hauptplatine Rev. 2.5 (Schaltplan + Layout)

Das Projekt über **Tumbler2_Redesign.kicad_pro** in KiCad 10 öffnen. **Tumbler2_Redesign.pdf** zeigt die acht aktuellen Blätter (Stand Rev. 2.5, 19.11.2026).

- Blatt 2: USB-C-Freigabe, 2S-Ladegerät, VBUS-Erkennung. Blatt 7: Pack, Verpolschutz, Schalter, Fahrabschaltung und Spannungsregler.
- Blatt 5: ICM-42670-P, TB6612FNG, Motorencoder und externer Ultraschall. Blatt 8: I²C-Multiplexer TCA9548A und Lötpads J8–J15 für acht ToF-Sensoren (VL53L0X/GY-530).
- Blatt 7, Block 05: **2S/3S-Brücken** R87, R88, R89, R92 (0 Ω) mit R90/R91 und D14.
- README_Schaltplan.md: 2S/3S-Umbau mit Rechnung, Betriebsarten, Stecker, Adressen, Firmware und offene Hardwaretests. Stueckliste.csv nennt Wert, Bestückung, Footprint und Spezifikation. Pinbelegung.csv beschreibt den bestehenden Liniensensor.
- **Rev. 2.5b (28.11.2026): bestellfertig für JLCPCB.**
  - BQ25886-Leistungsschleife kompakt: C36/C37 (SYS) direkt an Pin 15/16, L3 ~2 mm vom SW-Pin, C40 (BAT) nah, C30 (BTST) und C31 (REGN) direkt am IC, R49/R50 jetzt 0402 unter U12. C72 (1 µF) direkt an U9-Eingang.
  - Nicht lieferbare Teile ersetzt: **U2 AP63201WU-7** (einstellbar) mit Teiler **R93 47k / R94 15k** → 3,31 V; **U14 TLV3011** (Open-Drain) → **R55 jetzt Pull-up nach USB_3V3**; **L3 XEL4030-102MEC** (gleicher Footprint); C17 330 µF/25 V SMD 10×10; D2 rote Basic-LED; WS2812B-2020-V6.
  - Kosten: Kondensatoren auf Basic-Teile umgestellt, C1/C3/C6/C7/C25/C26/C65 auf eine Teilenummer (22 µF/25 V 1210). Alle SMD-Teile mit LCSC-Nummer, R5/R6 hatten vorher die Nummer eines 4,7-k-Widerstands.
  - J8–J15 neuer Footprint `Tumbler2:TOF_Wire_1x04_P2.54mm` (enger Courtyard), DRC-Regeldatei `Tumbler2_Redesign.kicad_dru` für J4 und die U3-Antenne.
  - Bestückungstexte kleiner Bauteile auf der Oberseite ausgeblendet (lagen auf Pads), dafür `Fertigung/Bestueckungsplan_oben/unten.pdf`.
  - KiCad 10.0.7: **ERC 0, DRC 0 Fehler, 0 offene Verbindungen, 0 Paritätsfehler.** Restliche 69 Warnungen sind Kosmetik (Siebdruck an Footprint-Grafiken/Rand, geänderte Testpunkt-Footprints, 5 Leiterbahnenden auf Padmitte).
  - Fertigung: `Fertigung/README.md` (Economic nur oben + Unterseite selbst löten, oder Standard beidseitig).
- **Rev. 2.5a (26.11.2026): Korrekturen vor der JLC-Bestellung.**
  - J12/J13 (ToF CH4/CH5) um 2,54 mm nach rechts: Die Lötstellen J12.1/J13.1 lagen 4,7/4,5 mm neben H4 und damit auf der Gehäusestütze (Ø 11 mm). Jetzt ≥ 7,0 mm Abstand. R79/R81 (Pull-ups) dafür auf freie Plätze der Unterseite versetzt. Mechanik/Gehauese_Bezugspunkte.csv angepasst.
  - Keine Vias mehr in Lötpads von Signalen (vorher R73.2, J6.4, U3 Pin 2 und 39, GND an J6.2/J7.2/D14.2). Nur die Wärme-Vias in den Thermalpads von U3 (Pin 41) und U12 (Pin 25) bleiben bewusst.
  - Alle Texte auf der Unterseite gespiegelt (vorher 78 spiegelverkehrte Bestückungstexte).
  - J1-Wert „Akku 2S/3S“. Auslieferung bleibt 2S: R87/R88/R89/R92 = 0 Ω bestückt.
  - KiCad 10.0.7: ERC 0, 0 offene Verbindungen, 0 Paritätsfehler. Bekannt/akzeptiert: 8 Pad-zu-NPTH-Abstände an J4 (Hersteller-Footprint, im JLC-DFM-Check ansehen), 6 Courtyard-Überlappungen ohne Kupferkonflikt.
  - **Bei JLC bestellen mit Innenlagen 1 oz** (Standard ist 0,5 oz): Motor- und Akkuleitungen laufen teilweise auf In2.Cu.
  - (Die damals offenen Punkte BQ25886-Schleife und U9-Eingangskondensator sind in Rev. 2.5b erledigt.)
- **Rev. 2.5 (19.11.2026): Akku 2S oder 3S.** Vier 0-Ω-Brücken auf der Unterseite (Kasten „2S | 3S“ unter U16): **alle bestückt = 2S** (Auslieferung, alte JST-XH-Akkus unverändert), **alle entfernt = 3S – R87 zuerst!**
  - R87 trennt den Lader (BQ25886 BAT, abs. max. 12 V) bei 3S ab (neues Netz CHG_BAT).
  - R88/R91: LTC4365-OV 8,75 V (2S) bzw. 13,52 V (3S). UV bleibt 5,50 V. In 2S-Stellung sperrt der LTC einen falsch gesteckten 3S-Akku.
  - R89/R90: Fahrfreigabe TPS3700 6,42/6,00 V (2S) bzw. 9,66/9,03 V (3S).
  - D1 jetzt SMBJ13A, zusätzlich D14 SMBJ8.5A über R92 (nur 2S). C17 220 µF/25 V, C63 100 nF/25 V.
  - Leistungsbahnen BAT_RAW, PROT_SRC, BAT_FUSED, PACK_SAFE, VBAT_SW überwiegend auf 0,6–0,65 mm verbreitert, wo der Abstand es zulässt (Motornetze M1/M2 meist noch 0,4 mm).
  - DRC-Korrekturen aus der Testkopie übernommen (SDA5-Verbindung, J4-VBUS-Brücke, ENCB_B aus der Antennensperrfläche, doppelte Via, Netznamen/Felder), Abstandsregel 0,125 mm. ERC-Kosmetik in peripherals (Encoder-Stummel) behoben.
  - Prüfung mit kicad-cli: **ERC 0, DRC 0 offene Verbindungen, 0 Abstands-, 0 Paritätsfehler.** Verbleibend: 8 × Lochabstand am USB-C-Footprint J4 (Herstellerfootprint, akzeptiert) und 7 bekannte Courtyard-Überlappungen (J12/J13, H4–J12/J13, U9/J12, C41/U13, U11/C31, U3/J6).
  - Firmware: `Hinweise_Software_Rev2.5.md`, Issue-Entwurf `Issue_Software_2S3S_Akku.md`.
- Rev. 2.4b (18.11.2026): Akkustecker J1 von Molex Micro-Fit 4-polig auf JST XH 2-polig (B2B-XH-A) geändert, damit die vorhandenen 2S-Akkus direkt passen. Onboard-Laden ist ohne NTC gesperrt, die Akkus werden extern geladen.
- Rev. 2.4 (12.11.2026): 8 ToF-Ports J8–J15 (J12-Leiste ersetzt durch Lötpads J12–J15, Pull-ups R79–R86, Abblockung C69–C71 auf der Unterseite), Multiplexer-RESET MUX_RSTn an GPIO37, Schaltplanblätter übersichtlich neu gezeichnet (GND nach unten, 3,3 V/5 V nach oben). Firmware-Hinweise damals: Hinweise_Software_Rev2.4.md (jetzt im Backup-Ordner) und GitHub-Issue.
- Rev. 2.3 (11.11.2026): ToF-Vorgaben der Software umgesetzt – TCA9548A (8 Kanäle), J8–J11 als Lötpads für GY-530-Kabel (VIN = +5 V, GND, SCL, SDA), J12 für CH4–CH7, alle I²C-Pull-ups 2,2 kΩ an +3,3 V. 
- Rev. 2.2 (11.11.2026): Akkuspannungsmessung R77/R78/C67 an GPIO3, J3 mit TXD0/RXD0/EN/IO0, README um Ladestrom-Begründung und Bremstest ergänzt.
- Pruefung/ enthält den aktuellen ERC, die exportierte Netzliste und die Ergebnisse der Pinprüfungen. TumblerBasis.kicad_sym bindet die übernommenen KiCad-Basissymbole ans Projekt; Quellen/Lizenz siehe LICENSE_KiCad_Bibliotheken.txt.

**Layout Rev. 2.4/2.5:** 4 Lagen – F.Cu Signal, In1.Cu durchgehende GND-Fläche, In2.Cu Signal, B.Cu Signal (GND-Flächen auf allen Lagen, beim Öffnen mit **B** füllen). Alle Bauteile neu platziert und vollständig geroutet. Stand Rev. 2.5 mit KiCad-DRC (kicad-cli, Flächen neu gefüllt) geprüft, siehe oben.
- ESP32-S3 an der rechten Kante, Antenne ragt über die Platine hinaus; Kupfer-Sperrflächen neben der Antenne auf allen Lagen, unter dem Antennenteil des Moduls kein Kupfer auf F.Cu.
- Vorne (Unterkante): 8 RGB-LEDs D6–D13, Liniensensor-Stecker J2, ToF-Lötpads J8 (vorne), J12/J13 daneben. Rechte Roboterseite (linke Bildkante): J9–J11, USB-C J4. J14 an der Hinterkante, J15 hinten links neben J1.
- Platzierungsuebersicht.png und Gehauese_Bezugspunkte.csv (Ursprung links unten, Y nach oben) in Mechanik/ entsprechen diesem Stand.
- Vor der Fertigung in KiCad: Flächen füllen, DRC laufen lassen, Bestückungsdruck prüfen. Hinweis: Bereich J12/U13/H4 hat knappe Courtyards (Kupfer frei).
