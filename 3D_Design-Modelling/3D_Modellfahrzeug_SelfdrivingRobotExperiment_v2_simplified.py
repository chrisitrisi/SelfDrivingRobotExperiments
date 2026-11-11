# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric CAD Generator & Exporter:
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_simplified
(Modulare 2-Teile-Bauweise: Ebene 3.0 mm Trägerplatte + Prismatische 2.4 mm Kotflügel-Haube)
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

        # 1. Alle parametrischen Benutzervariablen (DFM & KiCad) anlegen
        user_params = design.userParameters
        params_list = [
            ("BASEPLATE_THICK", "3.0 mm", "Durchgehende ebene Grundplatte"),
            ("WALL_THICK", "2.4 mm", "Einheitliche Wandstärke (6 Linien @ 0.4 mm / 4 Linien @ 0.6 mm)"),
            ("CHASSIS_HEIGHT", "25.0 mm", "Einheitliche Wandhöhe Unterteil & PCB-Auflageebene"),
            ("PCB_THT_CLEARANCE", "5.0 mm", "Freier Isolationsabstand unter PCB für THT-Lötstellen"),
            ("PCB_PITCH_X", "65.0 mm", "KiCad Tumbler2_Redesign M3 Lochabstand X"),
            ("PCB_PITCH_Y", "64.0 mm", "KiCad Tumbler2_Redesign M3 Lochabstand Y"),
            ("LINESENSOR_PITCH_X", "68.0 mm", "KiCad Liniensensor M3 Lochabstand X"),
            ("INSERT_DIA", "4.0 mm", "M3 Heat-Set Insert Lochdurchmesser"),
            ("INSERT_DEPTH", "5.5 mm", "M3 Heat-Set Insert Einsenkungstiefe"),
            ("WHEEL_DIA", "66.0 mm", "Antriebsrad-Durchmesser"),
            ("WHEEL_WIDTH", "27.0 mm", "Antriebsrad-Breite"),
            ("WHEEL_CLEARANCE", "3.5 mm", "Garantierter Mindestabstand Rad zu Kotflügel/Gehäuse"),
            ("CORNER_FILLET_R", "2.0 mm", "Innenradius gegen Kerbwirkung (>= 1.5 mm)"),
            ("BED_CHAMFER", "0.5 mm", "45-Grad Fase gegen Elefantenfuß am Druckbett"),
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
        step_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_simplified.step")
        f3d_path  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_simplified.f3d")

        root = design.rootComponent
        root.name = "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_simplified"

        if os.path.exists(step_path):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(step_path)
            import_mgr.importToTarget(step_opts, root)

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(f3d_path)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2_simplified erfolgreich erstellt!\n\n"
                f"- Modulare 2-Teile-Bauweise (Untere 3.0 mm Trägerplatte + Obere 2.4 mm Kotflügel-Haube)\n"
                f"- Native Fusion 360 Datei gespeichert unter:\n  {f3d_path}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
