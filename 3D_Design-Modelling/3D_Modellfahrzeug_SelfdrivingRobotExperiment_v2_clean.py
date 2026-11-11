# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric CAD Generator & Exporter:
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_clean
(Praktisches Flat-Bed Chassis: Offenes Heck, 3.0 mm Basis, 20.0 mm Wanne, 5.0 mm THT-Freiraum)
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
            ("LINESENSOR_PITCH_X", "68.0 mm", "KiCad Liniensensor M3 Lochabstand X"),
            ("INSERT_DIA", "4.0 mm", "M3 Heat-Set Insert Lochdurchmesser"),
            ("INSERT_DEPTH", "5.5 mm", "M3 Heat-Set Insert Tiefe"),
            ("REAR_WIDTH", "120.0 mm", "Heckbreite Motorplattform (100% offener Flat-Bed)"),
            ("REAR_LENGTH", "55.0 mm", "Hecktiefe Motorplattform"),
            ("FRONT_WIDTH", "70.0 mm", "Vorderwagen-Breite"),
        ]

        for name, expr, comment in params_list:
            if not user_params.itemByName(name):
                user_params.add(
                    name,
                    adsk.core.ValueInput.createByString(expr),
                    "mm",
                    comment
                )

        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        step_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_clean.step")
        f3d_path  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_clean.f3d")

        root = design.rootComponent
        root.name = "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_clean"

        if os.path.exists(step_path):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(step_path)
            import_mgr.importToTarget(step_opts, root)

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(f3d_path)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_clean erfolgreich erstellt!\n\n"
                f"- Flat-Bed Chassis mit 100% freiem Heck für Motoren und Räder\n"
                f"- 65x64 mm KiCad-Raster mit M3 Heat-Set Domen (Z=25mm, 5mm THT-Luft)\n"
                f"- Datei gespeichert unter:\n  {f3d_path}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
