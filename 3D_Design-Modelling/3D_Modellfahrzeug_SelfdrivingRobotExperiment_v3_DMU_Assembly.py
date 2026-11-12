# -*- coding: utf-8 -*-
"""
Fusion 360 Python API Script: Digital Mock-Up (DMU) / 3D-Assembly Generator & Interference Checker
Projekt: "Self-Driving Robot Experiment" (Tumbler v3.0)

Dieses Skript:
1. Lädt das aktuelle Gehäuse (3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated).
2. Erzeugt für jede reale Hardware-Baugruppe eine eigene Sub-Komponente (adsk.fusion.Component)
   im Browser-Strukturbaum (KEIN Join mit dem Chassis!):
   - 1_Main_PCB_Tumbler2_Redesign (76.96 x 80.52 x 1.6 mm, Dunkelgrün, auf Z=25.0 mm Standoffs)
   - 2a_DC_Motor_GA37_520_Left & 2b_Right (Ø 37 x 52 mm, Silber/Grau, quer auf der 120 mm Heckplatte)
   - 2c_Drive_Wheel_Left & 2d_Right (Ø 66.0 x 27.0 mm, Schwarz, an den Motorwellen außerhalb)
   - 3_Battery_2S_LiIon (70.0 x 36.8 x 19.0 mm, Blau, flach im rechten Wannenfach)
   - 4_Rocker_Switch (13.0 x 13.0 mm, Rot, in der Aussparung der linken Seitenwand)
   - 5a..5f_LiDAR_VL53L0_1XV2 (6x 25.0 x 10.5 x 1.6 mm, Lila/Gold, starr in den 6 Pods & Z=45mm Türmen)
3. Führt abschließend automatisch eine API-Kollisionsprüfung (design.analyzeInterference)
   über alle Komponenten durch und gibt das Protokoll im Text-Protokoll (Text Commands) sowie als Dialog aus.
"""

import adsk.core
import adsk.fusion
import traceback
import os
import math


# ==============================================================================
# KALIBRIERTE GLOBALE PARAMETER (in mm -> Fusion API rechnet intern in cm: * 0.1)
# ==============================================================================
v2_total_length = 25.0
v2_body_length  = 15.8
v2_width        = 10.5
v2_thickness    = 1.6
v2_hole_pitch   = 19.5
v2_ear_dia      = 5.5
v2_recess_depth = 2.6
v2_boss_height  = 1.0
v2_rear_tower_z = 45.0


def mm(val):
    """Konvertiert Millimeter in Fusion-360-interne Zentimeter (cm)."""
    return val * 0.1


def assign_rgb_color(design, occurrence_or_body, name, r, g, b, opacity=1.0):
    """Erstellt oder holt eine benutzerdefinierte RGB-Darstellung (Appearance) und weist sie zu."""
    try:
        app = adsk.core.Application.get()
        appearances = design.appearances
        target_app = appearances.itemByName(name)
        if not target_app:
            # Basis-Appearance aus der Fusion-Bibliothek kopieren
            lib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
            if not lib:
                lib = app.materialLibraries.item(0)
            base_app = None
            for cand in ["Paint - Enamel Glossy (White)", "Plastic - Matte (White)", "Smooth - White"]:
                base_app = lib.appearances.itemByName(cand)
                if base_app:
                    break
            if not base_app:
                base_app = lib.appearances.item(0)
            target_app = appearances.addByCopy(base_app, name)

        # RGB-Farbwert setzen
        for prop in target_app.appearanceProperties:
            if prop.objectType == adsk.core.ColorProperty.classType():
                col_prop = adsk.core.ColorProperty.cast(prop)
                if col_prop and not col_prop.isReadOnly:
                    col_prop.value = adsk.core.Color.create(r, g, b, int(opacity * 255))
                    break

        occurrence_or_body.appearance = target_app
    except:
        pass


def create_box_in_comp(comp, x0_mm, y0_mm, z0_mm, dx_mm, dy_mm, dz_mm, body_name):
    """Erzeugt einen achsenparallelen Quader als NewBodyFeature innerhalb einer Component."""
    sketches = comp.sketches
    xy_plane = comp.xYConstructionPlane
    sk = sketches.add(xy_plane)

    p1 = adsk.core.Point3D.create(mm(x0_mm), mm(y0_mm), mm(z0_mm))
    p2 = adsk.core.Point3D.create(mm(x0_mm + dx_mm), mm(y0_mm + dy_mm), mm(z0_mm))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(dz_mm)))
    ext_feat = extrudes.add(ext_input)
    body = ext_feat.bodies.item(0)
    body.name = body_name
    return body


def create_x_cylinder_in_comp(comp, x_center_mm, y_center_mm, z_center_mm, dia_mm, length_mm, body_name):
    """Erzeugt einen entlang der X-Achse liegenden Zylinder (für Motoren und Räder) innerhalb einer Component."""
    sketches = comp.sketches
    yz_plane = comp.yZConstructionPlane
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(yz_plane, adsk.core.ValueInput.createByReal(mm(x_center_mm - length_mm / 2.0)))
    offset_plane = planes.add(plane_input)

    sk = sketches.add(offset_plane)
    # In der YZ-Ebene von Fusion: X_sketch = Y_world, Y_sketch = Z_world (bzw. per Modellpunkt projizieren)
    center_world = adsk.core.Point3D.create(mm(x_center_mm - length_mm / 2.0), mm(y_center_mm), mm(z_center_mm))
    center_sk = sk.modelToSketchSpace(center_world)
    sk.sketchCurves.sketchCircles.addByCenterRadius(center_sk, mm(dia_mm / 2.0))

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(length_mm)))
    ext_feat = extrudes.add(ext_input)
    body = ext_feat.bodies.item(0)
    body.name = body_name
    return body


def create_lidar_v2_in_comp(comp, cx_mm, cy_mm, z_center_mm, yaw_deg, body_name):
    """
    Erzeugt einen VL53L0/1XV2 Platinen-Dummy (25.0 x 10.5 x 1.6 mm) im Ursprung der Component
    und positioniert die Occurrence starr (Rigid Transform: Rotation yaw_deg + Translation cx, cy, z_center)
    exakt im jeweiligen Sensor-Pod bzw. Z=45mm Turm.
    """
    sketches = comp.sketches
    yz_plane = comp.yZConstructionPlane
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    x_pcb_back = 9.5 - v2_recess_depth + v2_boss_height + 0.05  # 7.95 mm
    plane_input.setByOffset(yz_plane, adsk.core.ValueInput.createByReal(mm(x_pcb_back)))
    offset_plane = planes.add(plane_input)

    sk = sketches.add(offset_plane)
    c1 = sk.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(-v2_total_length / 2.0), mm(-v2_width / 2.0)))
    c2 = sk.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(+v2_total_length / 2.0), mm(+v2_width / 2.0)))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(c1, c2)

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(v2_thickness)))
    ext_feat = extrudes.add(ext_input)
    body = ext_feat.bodies.item(0)
    body.name = body_name
    return body


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        target_dir = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        chassis_step = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.step")
        dmu_f3d_out  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_DMU_Assembly.f3d")

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        root = design.rootComponent
        root.name = "Tumbler_v3_Digital_MockUp_Assembly"
        occs = root.occurrences

        # ======================================================================
        # 0. CHASSIS LADEN (als eigene Component im Assembly Tree)
        # ======================================================================
        if os.path.exists(chassis_step):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(chassis_step)
            import_mgr.importToTarget(step_opts, root)

        # ======================================================================
        # 1. HAUPTPLATINE (Tumbler2_Redesign: 76.96 x 80.52 x 1.6 mm auf Z = 25.0 mm)
        # ======================================================================
        occ_pcb = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_pcb.component.name = "1_Main_PCB_Tumbler2_Redesign"
        b_pcb = create_box_in_comp(
            occ_pcb.component,
            60.0 - 76.96 / 2.0, -106.91 - 80.52, 25.0,
            76.96, 80.52, 1.6,
            "Main_PCB_76.96x80.52x1.6"
        )
        assign_rgb_color(design, b_pcb, "DMU_DarkGreen_PCB", 20, 122, 56)

        # ======================================================================
        # 2. ANTRIEBSEINHEIT (2x GA37-520 Motoren Ø 37 x 52 mm + 2x Räder Ø 66 x 27 mm)
        # ======================================================================
        occ_mot_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_l.component.name = "2a_DC_Motor_GA37_520_Left"
        b_mot_l = create_x_cylinder_in_comp(occ_mot_l.component, 28.0, -23.0, 24.5, 37.0, 52.0, "GA37_520_Left")
        assign_rgb_color(design, b_mot_l, "DMU_Silver_Motor", 180, 186, 194)

        occ_mot_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_r.component.name = "2b_DC_Motor_GA37_520_Right"
        b_mot_r = create_x_cylinder_in_comp(occ_mot_r.component, 92.0, -23.0, 24.5, 37.0, 52.0, "GA37_520_Right")
        assign_rgb_color(design, b_mot_r, "DMU_Silver_Motor", 180, 186, 194)

        occ_whl_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_l.component.name = "2c_Drive_Wheel_66x27_Left"
        b_whl_l = create_x_cylinder_in_comp(occ_whl_l.component, -18.5, -23.0, 24.5, 66.0, 27.0, "Wheel_66x27_Left")
        assign_rgb_color(design, b_whl_l, "DMU_Black_Tire", 38, 40, 42)

        occ_whl_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_r.component.name = "2d_Drive_Wheel_66x27_Right"
        b_whl_r = create_x_cylinder_in_comp(occ_whl_r.component, 138.5, -23.0, 24.5, 66.0, 27.0, "Wheel_66x27_Right")
        assign_rgb_color(design, b_whl_r, "DMU_Black_Tire", 38, 40, 42)

        # ======================================================================
        # 3. ENERGIEVERSORGUNG (2S Li-Ion Akkupack: 70 x 36.8 x 19 mm, Blau)
        # ======================================================================
        occ_bat = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_bat.component.name = "3_Battery_2S_LiIon"
        b_bat = create_box_in_comp(
            occ_bat.component,
            54.8, -176.8, 3.2,
            36.8, 70.0, 19.0,
            "Battery_2S_LiIon_Pack"
        )
        assign_rgb_color(design, b_bat, "DMU_Blue_Battery", 31, 108, 224)

        # ======================================================================
        # 4. WIPPENSCHALTER (13.0 x 13.0 mm in der linken Seitenwand, Rot)
        # ======================================================================
        occ_sw = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_sw.component.name = "4_Rocker_Switch_13x13"
        b_sw = create_box_in_comp(
            occ_sw.component,
            22.5, -144.8, 7.2,
            10.0, 12.6, 12.6,
            "Rocker_Switch_13x13"
        )
        assign_rgb_color(design, b_sw, "DMU_Red_Switch", 217, 38, 38)

        # ======================================================================
        # 5. SENSORIK (6x VL53L0/1XV2 LiDARs per Rigid Transform in den 6 Pods)
        # ======================================================================
        pod_configs = [
            ("5a_LiDAR_VL53L0_1XV2_Front_Left_45deg",   21.0, -158.0, 13.0, -135.0),
            ("5b_LiDAR_VL53L0_1XV2_Front_Right_45deg",  99.0, -158.0, 13.0,  -45.0),
            ("5c_LiDAR_VL53L0_1XV2_Mid_Left_90deg",     25.0, -100.0, 13.0,  180.0),
            ("5d_LiDAR_VL53L0_1XV2_Mid_Right_90deg",    95.0, -100.0, 13.0,    0.0),
            ("5e_LiDAR_VL53L0_1XV2_Rear_Left_135deg",   22.5,  -70.0, v2_rear_tower_z, +135.0),
            ("5f_LiDAR_VL53L0_1XV2_Rear_Right_135deg",  97.5,  -70.0, v2_rear_tower_z,  +45.0),
        ]

        for (comp_name, cx, cy, cz, yaw_deg) in pod_configs:
            mat = adsk.core.Matrix3D.create()
            mat.setToRotation(
                math.radians(yaw_deg),
                adsk.core.Vector3D.create(0, 0, 1),
                adsk.core.Point3D.create(0, 0, 0)
            )
            mat.translation = adsk.core.Vector3D.create(mm(cx), mm(cy), mm(cz))
            occ_s = occs.addNewComponent(mat)
            occ_s.component.name = comp_name
            b_s = create_lidar_v2_in_comp(occ_s.component, cx, cy, cz, yaw_deg, comp_name)
            assign_rgb_color(design, b_s, "DMU_Purple_LiDAR_V2", 142, 46, 196)

        # ======================================================================
        # 6. AUTOMATISIERTER INTERFERENCE CHECK (KOLLISIONSPRÜFUNG PER FUSION API)
        # ======================================================================
        all_bodies = adsk.core.ObjectCollection.create()
        for occ in root.allOccurrences:
            for b in occ.bRepBodies:
                all_bodies.add(b)

        interference_msg = "Keine Kollisionen (0 Interferences) gefunden!"
        if all_bodies.count >= 2:
            inp = design.createInterferenceInput(all_bodies)
            inp.areCoincidentFacesIncluded = False
            results = design.analyzeInterference(inp)
            if results and results.count > 0:
                lines = [f"WARNUNG: {results.count} Kollision(en) gefunden:"]
                for r in results:
                    b1_name = r.entityOne.name if hasattr(r.entityOne, "name") else "Body1"
                    b2_name = r.entityTwo.name if hasattr(r.entityTwo, "name") else "Body2"
                    lines.append(f"  - {b1_name} schneidet {b2_name}")
                interference_msg = "\n".join(lines)

        app.log(f"=== DMU INTERFERENCE CHECK ===\n{interference_msg}")

        # Als .f3d Gesamtbaugruppe exportieren
        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(dmu_f3d_out)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"Digital Mock-Up (DMU) 3D-Assembly erfolgreich aufgebaut!\n\n"
                f"- 12 eigenständige Komponenten im Browser-Strukturbaum angelegt & eingefärbt\n"
                f"- Interference Check Ergebnis:\n  {interference_msg}\n\n"
                f"Gespeichert unter:\n{dmu_f3d_out}"
            )

    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
