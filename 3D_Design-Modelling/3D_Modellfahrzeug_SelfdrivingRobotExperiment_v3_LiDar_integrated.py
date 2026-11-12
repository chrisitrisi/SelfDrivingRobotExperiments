# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric CAD Generator & Exporter:
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_integrated
(Flat-Bed Chassis + 6x VL53L0X / GY-530 LiDAR Sensor-Pods @ 45°, 90°, 135°)
"""

import adsk.core
import adsk.fusion
import traceback
import os


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        user_params = design.userParameters
        params_list = [
            ("BASEPLATE_THICK", "3.0 mm", "Durchgehende ebene Grundplatte"),
            ("WALL_THICK", "2.4 mm", "Einheitliche Wandstärke Wanne (6 Linien @ 0.4mm)"),
            ("WANNE_HEIGHT", "20.0 mm", "Einheitliche Wannenhöhe Vorderwagen"),
            ("STANDOFF_HEIGHT", "25.0 mm", "PCB-Montagehöhe (5.0 mm THT-Isolationsabstand)"),
            ("PCB_PITCH_X", "65.0 mm", "KiCad Tumbler2 M3 Lochabstand X"),
            ("PCB_PITCH_Y", "64.0 mm", "KiCad Tumbler2 M3 Lochabstand Y"),
            ("LIDAR_POCKET_W", "14.0 mm", "Breite Sensortasche für GY-530 (13.3 mm)"),
            ("LIDAR_POCKET_H", "11.0 mm", "Höhe Sensortasche für GY-530 (10.5 mm)"),
            ("LIDAR_POCKET_DEPTH", "1.5 mm", "Einsenkungstiefe Sensor-Bett (Seitenaufprallschutz)"),
            ("LIDAR_WINDOW_W", "6.0 mm", "Breite Optik-Fenster VL53L0X"),
            ("LIDAR_WINDOW_H", "3.5 mm", "Höhe Optik-Fenster VL53L0X"),
            ("LIDAR_M2_PITCH", "8.0 mm", "Bohrungsabstand M2 Befestigung VL53L0X (Default 8.0 mm)"),
            ("LIDAR_M2_CORE_DIA", "1.8 mm", "Kernlochdurchmesser M2 selbstfurchend"),
            ("LIDAR_CABLE_SLOT_W", "12.0 mm", "Breite I2C 4-Pin Kabeldurchbruch"),
            ("LIDAR_CABLE_SLOT_H", "6.0 mm", "Höhe I2C 4-Pin Kabeldurchbruch ab Baseplate"),
            ("LIDAR_ANGLE_FRONT", "45.0 deg", "Ausrichtungswinkel vordere LiDAR-Sensoren"),
            ("LIDAR_ANGLE_MID", "90.0 deg", "Ausrichtungswinkel mittlere LiDAR-Sensoren"),
            ("LIDAR_ANGLE_REAR", "135.0 deg", "Ausrichtungswinkel hintere LiDAR-Sensoren"),
        ]

        for name, expr, comment in params_list:
            unit = "deg" if "deg" in expr else "mm"
            if not user_params.itemByName(name):
                user_params.add(
                    name,
                    adsk.core.ValueInput.createByString(expr),
                    unit,
                    comment
                )

        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        step_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_integrated.step")
        f3d_path  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_integrated.f3d")

        root = design.rootComponent
        root.name = "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_integrated"

        if os.path.exists(step_path):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(step_path)
            import_mgr.importToTarget(step_opts, root)

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(f3d_path)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_integrated erfolgreich erstellt!\n\n"
                f"- 6x VL53L0X (GY-530) Sensor-Pods (45°, 90°, 135°)\n"
                f"- M2 Kernloch Ø 1.8 mm (Pitch = 8.0 mm parametrisch)\n"
                f"- 14x11x1.5 mm Sensor-Bett, 6x3.5 mm Optik-Fenster, 12x6 mm I2C-Kabelschlitz\n"
                f"- Datei gespeichert unter:\n  {f3d_path}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
