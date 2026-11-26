# Hardware figures (chapter 3)

All `*.pdf` here are vector exports from KiCad 10 (`kicad-cli … export svg`, cropped via the SVG viewBox,
converted with `rsvg-convert -f pdf`). Annotations are drawn in LaTeX with the `kicadannot` environment
(`hardware_macros.tex`) in KiCad millimetre coordinates. The crop window below must be passed to `kicadannot`.

| File | Source | Crop window (x0,y0)-(x1,y1) mm |
|---|---|---|
| sch25_* (full sheets) | Rev 2.5 schematic | full sheet |
| sch25_power_ltc, sch24b_power_ltc | power sheet | (140,20)-(275,70) |
| sch25_power_tps, sch24b_power_tps | power sheet | (205,70)-(335,125) |
| sch25_power_bridges | power sheet | (185,258)-(425,345) |
| sch25_power_input / _bucks | power sheet | (15,20)-(112,80) / (15,180)-(335,250) |
| sch_predrc_int1, sch25_int1 | peripherals sheet | (110,200)-(180,235) |
| pcb25_top/bottom/in1/in2, pcb2l_top/bottom | Rev 2.5 / 2-layer branch | (112.9,63.9)-(191.7,146.2) |
| pcb25_bridges | Rev 2.5 B.Cu | (160,71)-(182,93) |
| pcb24b_power, pcb25_power | F.Cu, zones unfilled | (124,64.5)-(178,100) |
| pcb24_j1_molex, pcb25_j1 | F.Cu | (122,64.5)-(148,84) |
| pcb24b_j4, pcb25_j4 | F.Cu | (116.5,102)-(123,112) |
| pcb24b_antenna, pcb25_antenna | B.Cu | (183.5,117)-(191,122) |
| ls_r2_top / ls_r3_top | line sensor R2 / R3 | (-0.83,-0.83)-(76.02,32.02) / (75.88,50.18)-(152.73,83.03) |
| ls_r2_top_q1 / ls_r3_top_q1 | line sensor | (11.97,17.97)-(30.97,31.97) / (88.68,68.98)-(107.68,82.98) |
| chassis_top | STL edge drawing | (-9.86,0)-(129.86,274.36), coords (X, 44.86−Y) |
| print_bed | sliced 3MF, P1S | (0,0)-(260,260), coords (x+2, 258−y) |
| old_board_schematic | predecessor project | – |
| render25_top/bottom.png | KiCad 3D render (raster) | – |

Export scripts: `~/School/DA/_doku_export/werkzeuge/` (kicad/, bambu_p1s/).
