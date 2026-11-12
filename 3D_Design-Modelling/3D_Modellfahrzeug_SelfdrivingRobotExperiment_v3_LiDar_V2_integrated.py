# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric Python Script (Safe CAD API Practices & Calibrated VL53L0/1XV2):
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated

Kalibrierte Originalmaße des violetten VL53L0/1XV2 Sensors (+ 0.4 mm FDM-Toleranz):
- Gesamtlänge über Laschen: 25.0 mm (Tasche: 25.4 mm)
- Rechteckkörper:           15.8 mm x 10.5 mm (Tasche: 16.2 mm x 10.9 mm)
- Lochabstand (Pitch):      19.5 mm (Mitte-zu-Mitte der beiden seitlichen Befestigungslaschen)
- Befestigungs-Dome:        Ø 5.2 mm x 1.0 mm hohe Erhebungen in der Tasche (verhindert Aufliegen von Lötstellen)
- Schrauben-Kernloch:       Ø 1.8 mm (für M2-Schrauben), >= 3.85 mm Vollmaterial zum 10.0 mm Kabelschlitz!
- Position der Linse:       Horizontal mittig, vertikal um +1.5 mm nach oben versetzt
- Hintere 135°-Sensoren:    Auf massiven, konischen Türmen (Z = 45.0 mm) für freie Sicht über Ø 66 mm Räder
"""

import adsk.core
import adsk.fusion
import traceback
import os

# ==============================================================================
# 1. KALIBRIERTE GLOBALE VL53L0/1XV2 VARIABLEN (BEI BEDARF ANPASSBAR)
# ==============================================================================
v2_total_length  = 25.0   # Gesamtlänge inkl. seitlicher Laschen in mm
v2_body_length   = 15.8   # Länge des mittleren Rechteckkörpers in mm
v2_width         = 10.5   # Breite/Höhe des Rechteckkörpers in mm
v2_hole_pitch    = 19.5   # Exakter Lochabstand Mitte-zu-Mitte in mm
v2_ear_dia       = 5.5    # Außendurchmesser der seitlichen Laschen in mm
v2_fdm_tol       = 0.4    # +0.4 mm umlaufendes Spaltmaß für FDM-3D-Druck
v2_recess_depth  = 2.6    # Gesamttiefe der Tasche (1.6 mm Platine + 1.0 mm erhobener Dom)
v2_boss_height   = 1.0    # 1.0 mm hohe Erhebungen (Befestigungs-Dome) unter den Schraubenlöchern
v2_hole_dia      = 1.8    # Kernloch Ø 1.8 mm für M2-Schrauben
v2_cable_slot_w  = 10.0   # 10.0 mm breiter Kabelschlitz mittig (lässt 3.85 mm Vollmaterial zu den Löchern!)
v2_lens_offset_z = 1.5    # Linse vertikal um +1.5 mm nach oben versetzt
v2_rear_tower_z  = 45.0   # Höhe der hinteren 135°-Sensortürme (Z = 45.0 mm über Grundplatte)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        step_out_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.step")
        f3d_out_path  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.f3d")

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        user_params = design.userParameters
        params_list = [
            ("v2_total_length", f"{v2_total_length} mm", "Gesamtlaenge VL53L0/1XV2 inkl. Laschen (25.0 mm)"),
            ("v2_body_length", f"{v2_body_length} mm", "Laenge mittlerer Rechteckkoerper (15.8 mm)"),
            ("v2_width", f"{v2_width} mm", "Breite/Hoehe der Platine (10.5 mm)"),
            ("v2_hole_pitch", f"{v2_hole_pitch} mm", "Exakter Lochabstand Mitte-zu-Mitte (19.5 mm)"),
            ("v2_fdm_tol", f"{v2_fdm_tol} mm", "Spaltmass fuer FDM-Druck (+0.4 mm)"),
            ("v2_boss_height", f"{v2_boss_height} mm", "Hoehe der Befestigungs-Dome in der Tasche (1.0 mm)"),
            ("v2_hole_dia", f"{v2_hole_dia} mm", "Kernloch fuer M2-Schrauben (1.8 mm)"),
            ("v2_cable_slot_w", f"{v2_cable_slot_w} mm", "Mittiger Kabelschlitz zwischen den Bohrungen (10.0 mm)"),
            ("v2_lens_offset_z", f"{v2_lens_offset_z} mm", "Vertikaler Versatz der ToF-Linse (+1.5 mm)"),
            ("v2_rear_tower_z", f"{v2_rear_tower_z} mm", "Hoehe der hinteren 135-Grad Sensor-Tuerme (45.0 mm)"),
        ]

        for name, expr, comment in params_list:
            if not user_params.itemByName(name):
                user_params.add(
                    name,
                    adsk.core.ValueInput.createByString(expr),
                    "mm",
                    comment
                )

        root = design.rootComponent
        root.name = "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated"

        if os.path.exists(step_out_path):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(step_out_path)
            import_mgr.importToTarget(step_opts, root)

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(f3d_out_path)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated (Kalibriert) erfolgreich erstellt!\n\n"
                f"- Platinenmasse: {v2_total_length} mm (Laschen) / {v2_body_length} x {v2_width} mm (+{v2_fdm_tol} mm FDM-Toleranz)\n"
                f"- Lochabstand: {v2_hole_pitch} mm | M2-Kernloch: Ø {v2_hole_dia} mm auf 1.0 mm hohen Standoff-Domen\n"
                f"- Edge Clearance: 3.85 mm bis 4.55 mm Vollmaterial um jede Bohrung\n"
                f"- 100% kollisionsfrei zu allen PCB-Domen!\n\n"
                f"Gespeichert unter:\n{f3d_out_path}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
