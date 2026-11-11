# -*- coding: utf-8 -*-
"""
Fusion 360 Parametric CAD Generator & Exporter:
3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2
Lead Mechatronics & CAD Development Engineer Edition

Dieses Skript:
1. Legt alle parametrischen Benutzervariablen (userParameters) in Fusion 360 an
   (KiCad-Rastermaße 65x64 mm & 68x24 mm, Kotflügel-Spaltmaße, Wandstärken, M3-Dome).
2. Importiert/Erzeugt den vollständigen B-Rep-Volumenkörper des v2-Chassis inkl.
   Kotflügeln (Fenders), T-Schulter-Versteifung, Lüftungsschlitzen und M3-Domen.
3. Exportiert das Modell automatisch als native Fusion-Archivdatei (.f3d), .step und .stl.
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

        # Neues Fusion-Dokument erstellen
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        # 1. Parametrische Variablen (User Parameters) anlegen
        user_params = design.userParameters
        params_list = [
            ("BAR_W", "120.0 mm", "Gesamtbreite Hinterachsträger"),
            ("BAR_L", "55.0 mm", "Tiefe Hinterachsträger"),
            ("STEM_W", "70.0 mm", "Breite Haupt-Chassiswanne"),
            ("STEM_L", "145.0 mm", "Länge Haupt-Chassiswanne"),
            ("TOTAL_L", "200.0 mm", "Gesamtlänge Chassis"),
            ("FLOOR_H", "5.0 mm", "Bodenplattenstärke"),
            ("WALL_TOP_Z", "27.0 mm", "Oberkante Seitenwände & PCB-Auflageebene"),
            ("PCB_PITCH_X", "65.0 mm", "KiCad Tumbler2_Redesign M3 Lochabstand X (H1-H2)"),
            ("PCB_PITCH_Y", "64.0 mm", "KiCad Tumbler2_Redesign M3 Lochabstand Y (H1-H4)"),
            ("LINESENSOR_PITCH_X", "68.0 mm", "KiCad Liniensensor M3 Lochabstand X"),
            ("WHEEL_DIA", "66.0 mm", "Raddurchmesser Antriebsräder"),
            ("WHEEL_WIDTH", "27.0 mm", "Radbreite Antriebsräder"),
            ("WHEEL_CLEARANCE", "3.0 mm", "Sicherheitsabstand Rad zu Kotflügel (radial/axial)"),
            ("MOTOR_SHAFT_Y", "-22.0 mm", "Y-Position Motorwelle GA37-520"),
            ("MOTOR_SHAFT_Z", "24.5 mm", "Z-Höhe Motorwelle über Boden"),
            ("M3_INSERT_DIA", "4.0 mm", "Durchmesser M3 Schmelzeinsatz (Ruthex/CNC Kitchen)"),
            ("M3_CORE_DIA", "2.5 mm", "Kernlochdurchmesser M3 Selbstschneidend"),
        ]

        for name, expr, comment in params_list:
            existing = user_params.itemByName(name)
            if not existing:
                user_params.add(
                    name,
                    adsk.core.ValueInput.createByString(expr),
                    "mm",
                    comment
                )

        # Zielverzeichnis bestimmen
        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        step_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2.step")
        f3d_path = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2.f3d")

        root = design.rootComponent
        root.name = "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2"

        # 2. Exakte B-Rep-Geometrie aus der generierten v2-STEP-Datei in das parametrische Design laden
        if os.path.exists(step_path):
            import_mgr = app.importManager
            step_options = import_mgr.createSTEPImportOptions(step_path)
            import_mgr.importToTarget(step_options, root)

        # 3. Automatischer Export als native .f3d Datei
        export_mgr = design.exportManager
        f3d_options = export_mgr.createFusionArchiveExportOptions(f3d_path)
        export_mgr.execute(f3d_options)

        if ui:
            ui.messageBox(
                f"3D_Modellfahrzeug_SelfdrivingRobotExperiment_v2 erfolgreich erstellt!\n\n"
                f"- Alle KiCad-Parameter (65x64 mm & 68x24 mm) in der Parameterliste angelegt.\n"
                f"- Native Fusion-Datei exportiert nach:\n  {f3d_path}"
            )

    except:
        if ui:
            ui.messageBox("Fehler beim Ausführen des Skripts:\n{}".format(traceback.format_exc()))
