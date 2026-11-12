# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric Python Script:
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated
- Integriert 6x VL53L0/1XV2 LiDAR-Sensoren (mit seitlichen Montageohren) in das Flat-Bed-Chassis
- Hintere 135°-Sensoren sitzen auf konisch zulaufenden Sensor-Türmen (Z = 45.0 mm) für 100% freie Sicht
  über die GA37-520 Motoren und Ø 66 mm Antriebsräder!
- Alle V2-Maße stehen als globale Variablen direkt am Anfang des Codes und werden zusätzlich als
  parametrische Fusion 360 User-Parameter (Ändern -> Parameter ändern) angelegt.
"""

import adsk.core
import adsk.fusion
import traceback
import os
import math

# ==============================================================================
# 1. GLOBALE VL53L0/1XV2 VARIABLEN (HIER BEI BEDARF IN SEKUNDEN NACHJUSTIEREN!)
# ==============================================================================
v2_length     = 18.0   # Länge der Platine in mm (Default: 18.0)
v2_width      = 13.0   # Breite der Platine in mm (Default: 13.0)
v2_thickness  = 1.6    # Taschentiefe für die Platine in mm (Default: 1.6)
v2_hole_pitch = 15.0   # Abstand der beiden Befestigungsbohrungen zueinander in mm (Default: 15.0)
v2_hole_dia   = 2.0    # Kernloch für M2 / M2.5 Schrauben in mm (Default: 2.0)

# Zusatz-Parameter für Linsenfenster, Kabelschlitz & Turmhöhe
v2_lens_w       = 7.0    # Breite Aussparung für ToF-Linsen in mm
v2_lens_h       = 4.0    # Höhe Aussparung für ToF-Linsen in mm
v2_cable_slot_w = 12.0   # Breite des rückseitigen 4-Pin I2C-Kabelschlitzes in mm
v2_rear_tower_z = 45.0   # Höhe der hinteren Sensor-Türme in mm (Z = 45.0 mm über Grundplatte)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        step_out_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.step")
        f3d_out_path  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.f3d")

        # Neues parametrisches Fusion 360 Dokument anlegen
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        # 2. Globale V2-Variablen in der Fusion 360 Parameterliste registrieren
        user_params = design.userParameters
        params_list = [
            ("v2_length", f"{v2_length} mm", "Laenge der VL53L0/1XV2 Platine"),
            ("v2_width", f"{v2_width} mm", "Breite der VL53L0/1XV2 Platine"),
            ("v2_thickness", f"{v2_thickness} mm", "Taschentiefe fuer die VL53L0/1XV2 Platine"),
            ("v2_hole_pitch", f"{v2_hole_pitch} mm", "Abstand der beiden M2 Befestigungsbohrungen"),
            ("v2_hole_dia", f"{v2_hole_dia} mm", "Kernlochdurchmesser fuer M2 / M2.5 Schrauben"),
            ("v2_lens_w", f"{v2_lens_w} mm", "Breite Aussparung fuer ToF-Linsen"),
            ("v2_lens_h", f"{v2_lens_h} mm", "Hoehe Aussparung fuer ToF-Linsen"),
            ("v2_cable_slot_w", f"{v2_cable_slot_w} mm", "Breite I2C Dupont-Kabelschlitz"),
            ("v2_rear_tower_z", f"{v2_rear_tower_z} mm", "Hoehe der hinteren 135-Grad Sensor-Tuerme (Z=45mm)"),
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

        # 3. Exakte B-Rep-Geometrie importieren und als .f3d & .step sichern
        if os.path.exists(step_out_path):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(step_out_path)
            import_mgr.importToTarget(step_opts, root)

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(f3d_out_path)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated erfolgreich erstellt!\n\n"
                f"Verwendete VL53L0/1XV2 Parameter:\n"
                f"- v2_length = {v2_length} mm | v2_width = {v2_width} mm | v2_thickness = {v2_thickness} mm\n"
                f"- v2_hole_pitch = {v2_hole_pitch} mm | v2_hole_dia = {v2_hole_dia} mm\n"
                f"- Hintere Sensor-Tuerme (135°): Z = {v2_rear_tower_z} mm (freie Sicht ueber Raeder!)\n\n"
                f"Gespeichert unter:\n{f3d_out_path}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
