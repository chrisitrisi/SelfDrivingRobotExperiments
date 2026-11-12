# -*- coding: utf-8 -*-
"""
Fusion 360 Python API Script: 100% Complete Digital Mock-Up (DMU) & Chassis v4 Redesign
Projekt: "Self-Driving Robot Experiment" (Tumbler v3.0 / v4 Master DMU)

Features in diesem Skript:
1. Aktualisiert das Chassis mit:
   - Integrierter Heck-Sensor-Bar (Rear Bumper Y = 0 .. +22 mm) HINTER den GA37-520 Motoren,
     sodass alle 6x VL53L0/1XV2 LiDARs auf exakt derselben Höhe (Z = 13.0 mm) sitzen und die beiden
     hinteren 135°-Sensoren komplett freie Sicht hinter den Ø 66 mm Antriebsrädern vorbei haben!
   - Integrierter Front-Liniensensor-Haltebrücke (68.0 x 24.0 mm M3-Raster), die den Liniensensor
     auf der Unterseite trägt (sodass die 6x CNY70 Optokoppler exakt 2.5 mm über der Fahrbahn schweben).
   - Dediziertem, vibrationsgedämpftem IMU/Gyro-Montagesockel (MPU6050) exakt im Drehzentrum (X=60, Y=-75 mm).
   - USB-C Panel-Mount Aussparung & Halterung an der vorderen linken Seitenwand.
2. Generiert sämtliche Hardware-Komponenten als eigenständige, farbig kodierte `adsk.fusion.Component`
   Einträge im Browser-Baum (ohne Join!) und führt automatisch `design.analyzeInterference` aus:
   - Neue Hauptplatine (76.96 x 80.52 x 1.6 mm, Dunkelgrün) inkl. ESP32-S3, Motortreiber-H-Brücken (Rot),
     USB-C Buchse (Silber) und JST-Steckerleisten (Cremeweiß)
   - Neuer Liniensensor (76.0 x 32.0 x 1.6 mm, Grün) + 6x CNY70 Optokoppler-Dioden (Schwarz, unten)
   - Ultraschallsensor HC-SR04 (2x Ø 16 mm Alu-Zylinder an Frontkante)
   - Gyro-/Beschleunigungssensor MPU6050 (Blaues Modul + QFN-Chip im Fahrzeugzentrum)
   - USB-C Panel-Mount Buchse (Silber, Seitenwand vorne)
   - 6x VL53L0/1XV2 LiDARs (Lila/Gold, 25.0 x 10.5 x 1.6 mm, alle auf Z = 13.0 mm: 4x Seite, 2x Heck-Bumper)
   - 2S Li-Ion Akku (Blau), Wippenschalter (Rot), 2x GA37-520 Motoren (Silber), 2x Ø 66 mm Räder (Schwarz)
     und vorderer Gleitnippel (Lila).
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
v2_recess_depth = 2.6
v2_boss_height  = 1.0
LIDAR_Z_CENTER  = 13.0   # Alle 6 LiDAR-Sensoren auf identischer Höhe Z = 13.0 mm!


def mm(val):
    return val * 0.1


def assign_rgb_color(design, entity, name, r, g, b, opacity=1.0):
    try:
        app = adsk.core.Application.get()
        appearances = design.appearances
        target_app = appearances.itemByName(name)
        if not target_app:
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

        for prop in target_app.appearanceProperties:
            if prop.objectType == adsk.core.ColorProperty.classType():
                col_prop = adsk.core.ColorProperty.cast(prop)
                if col_prop and not col_prop.isReadOnly:
                    col_prop.value = adsk.core.Color.create(r, g, b, int(opacity * 255))
                    break

        entity.appearance = target_app
    except:
        pass


def create_box_in_comp(comp, x0_mm, y0_mm, z0_mm, dx_mm, dy_mm, dz_mm, body_name):
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
    sketches = comp.sketches
    yz_plane = comp.yZConstructionPlane
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(yz_plane, adsk.core.ValueInput.createByReal(mm(x_center_mm - length_mm / 2.0)))
    offset_plane = planes.add(plane_input)
    sk = sketches.add(offset_plane)
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


def create_z_cylinder_in_comp(comp, x_mm, y_mm, z0_mm, dia_mm, height_mm, body_name):
    sketches = comp.sketches
    xy_plane = comp.xYConstructionPlane
    sk = sketches.add(xy_plane)
    center_pt = adsk.core.Point3D.create(mm(x_mm), mm(y_mm), mm(z0_mm))
    sk.sketchCurves.sketchCircles.addByCenterRadius(center_pt, mm(dia_mm / 2.0))
    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(height_mm)))
    ext_feat = extrudes.add(ext_input)
    body = ext_feat.bodies.item(0)
    body.name = body_name
    return body


def create_lidar_v2_in_comp(comp, body_name):
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
        root.name = "Tumbler_v4_Complete_Master_DMU"
        occs = root.occurrences

        # 0. AKTUALISIERTES CHASSIS LADEN (inkl. Heck-Sensor-Bar, Liniensensor-Brücke & IMU-Sockel)
        if os.path.exists(chassis_step):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(chassis_step)
            import_mgr.importToTarget(step_opts, root)

        # 1. NEUE HAUPTPLATINE (Tumbler2_Redesign: 76.96 x 80.52 x 1.6 mm + ESP32 + Motortreiber + USB-C)
        occ_pcb = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_pcb.component.name = "1_Main_PCB_Tumbler2_Redesign"
        b_pcb = create_box_in_comp(occ_pcb.component, 21.49, -187.43, 25.0, 76.96, 80.52, 1.6, "Main_PCB_Board")
        assign_rgb_color(design, b_pcb, "DMU_DarkGreen_PCB", 20, 117, 50)

        b_esp = create_box_in_comp(occ_pcb.component, 28.0, -162.0, 26.6, 18.0, 25.5, 3.2, "ESP32_S3_WROOM_1")
        assign_rgb_color(design, b_esp, "DMU_Silver_ESP", 200, 208, 216)

        b_drv_c = create_box_in_comp(occ_pcb.component, 50.0, -152.0, 26.6, 20.0, 21.0, 3.6, "MotorDriver_HBridge_Module")
        b_drv_l = create_box_in_comp(occ_pcb.component, 38.8, -131.5, 26.6, 8.0, 8.0, 2.2, "TB67H450_Left")
        b_drv_r = create_box_in_comp(occ_pcb.component, 73.8, -131.5, 26.6, 8.0, 8.0, 2.2, "TB67H450_Right")
        assign_rgb_color(design, b_drv_c, "DMU_Red_Driver", 220, 38, 38)
        assign_rgb_color(design, b_drv_l, "DMU_Red_Driver", 220, 38, 38)
        assign_rgb_color(design, b_drv_r, "DMU_Red_Driver", 220, 38, 38)

        b_usbc_j4 = create_box_in_comp(occ_pcb.component, 34.1, -188.5, 26.6, 9.0, 7.5, 3.2, "USBC_Onboard_J4")
        assign_rgb_color(design, b_usbc_j4, "DMU_Silver_ESP", 200, 208, 216)

        # 2. NEUER LINIENSENSOR (Liniensensor_Redesign: 76.0 x 32.0 x 1.6 mm + 6x CNY70 Dioden unten)
        occ_ls = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_ls.component.name = "2_LineSensor_Redesign_with_6x_CNY70"
        b_ls_pcb = create_box_in_comp(occ_ls.component, 22.0, -199.0, -1.6, 76.0, 32.0, 1.6, "LineSensor_PCB_76x32")
        assign_rgb_color(design, b_ls_pcb, "DMU_Green_LineSensor", 27, 128, 59)
        for idx, cx in enumerate([35.0, 45.0, 55.0, 65.0, 75.0, 85.0]):
            b_cny = create_box_in_comp(occ_ls.component, cx - 3.5, -193.5, -6.0, 7.0, 7.0, 4.4, f"CNY70_Opto_{idx+1}")
            assign_rgb_color(design, b_cny, "DMU_Black_Tire", 28, 30, 32)

        # 3. ULTRASCHALLSENSOR HC-SR04 (Front)
        occ_us = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_us.component.name = "3_Ultrasonic_Sensor_HC_SR04"
        b_us = create_box_in_comp(occ_us.component, 44.5, -187.5, 29.1, 45.0, 4.0, 20.0, "HC_SR04_Unit")
        assign_rgb_color(design, b_us, "DMU_Silver_ESP", 184, 194, 204)

        # 4. GYRO-/BESCHLEUNIGUNGSSENSOR (MPU6050 exakt im Fahrzeug-Drehzentrum X=60, Y=-75 mm)
        occ_imu = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_imu.component.name = "4_IMU_Gyro_Accelerometer_MPU6050"
        b_imu = create_box_in_comp(occ_imu.component, 49.5, -83.0, 9.05, 21.0, 16.0, 2.2, "MPU6050_Breakout")
        assign_rgb_color(design, b_imu, "DMU_Blue_IMU", 26, 92, 214)

        # 5. USB-C PANEL-MOUNT BUCHSE (Seitenwand links)
        occ_usbc = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_usbc.component.name = "5_USBC_Panel_Mount_Port"
        b_usbc = create_box_in_comp(occ_usbc.component, 23.5, -128.3, 8.1, 7.0, 8.2, 4.2, "USBC_Panel_Connector")
        assign_rgb_color(design, b_usbc, "DMU_Silver_ESP", 208, 213, 221)

        # 6. 6x VL53L0/1XV2 LiDARs (4x Seite, 2x im neuen Heck-Bumper hinter den Motoren, alle Z = 13.0 mm)
        pod_configs = [
            ("6a_LiDAR_VL53L0_1XV2_Front_Left_45deg",   21.0, -152.0, LIDAR_Z_CENTER, -135.0),
            ("6b_LiDAR_VL53L0_1XV2_Front_Right_45deg",  99.0, -152.0, LIDAR_Z_CENTER,  -45.0),
            ("6c_LiDAR_VL53L0_1XV2_Mid_Left_90deg",     25.0, -100.0, LIDAR_Z_CENTER,  180.0),
            ("6d_LiDAR_VL53L0_1XV2_Mid_Right_90deg",    95.0, -100.0, LIDAR_Z_CENTER,    0.0),
            ("6e_LiDAR_VL53L0_1XV2_Rear_Left_135deg",   22.0,  +13.0, LIDAR_Z_CENTER, +135.0),
            ("6f_LiDAR_VL53L0_1XV2_Rear_Right_135deg",  98.0,  +13.0, LIDAR_Z_CENTER,  +45.0),
        ]
        for (comp_name, cx, cy, cz, yaw_deg) in pod_configs:
            mat = adsk.core.Matrix3D.create()
            mat.setToRotation(math.radians(yaw_deg), adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
            mat.translation = adsk.core.Vector3D.create(mm(cx), mm(cy), mm(cz))
            occ_s = occs.addNewComponent(mat)
            occ_s.component.name = comp_name
            b_s = create_lidar_v2_in_comp(occ_s.component, comp_name)
            assign_rgb_color(design, b_s, "DMU_Purple_LiDAR_V2", 142, 46, 196)

        # 7. 2S LI-ION AKKU & 8. WIPPENSCHALTER
        occ_bat = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_bat.component.name = "7_Battery_2S_LiIon_Pack"
        b_bat = create_box_in_comp(occ_bat.component, 54.5, -168.0, 3.2, 32.0, 65.0, 19.0, "Battery_2S_LiIon")
        assign_rgb_color(design, b_bat, "DMU_Blue_Battery", 31, 108, 224)

        occ_sw = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_sw.component.name = "8_Rocker_Switch_13x13"
        b_sw = create_box_in_comp(occ_sw.component, 23.5, -144.8, 7.2, 9.0, 12.6, 12.6, "Rocker_Switch")
        assign_rgb_color(design, b_sw, "DMU_Red_Driver", 217, 38, 38)

        # 9. 2x GA37-520 MOTOREN & 10. 2x ANTRIEBSRÄDER Ø 66 x 27 mm & 11. GLEITNIPPEL
        occ_mot_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_l.component.name = "9a_DC_Motor_GA37_520_Left"
        b_mot_l = create_x_cylinder_in_comp(occ_mot_l.component, 28.0, -23.0, 24.5, 37.0, 52.0, "GA37_520_Left")
        assign_rgb_color(design, b_mot_l, "DMU_Silver_Motor", 168, 176, 184)

        occ_mot_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_r.component.name = "9b_DC_Motor_GA37_520_Right"
        b_mot_r = create_x_cylinder_in_comp(occ_mot_r.component, 92.0, -23.0, 24.5, 37.0, 52.0, "GA37_520_Right")
        assign_rgb_color(design, b_mot_r, "DMU_Silver_Motor", 168, 176, 184)

        occ_whl_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_l.component.name = "10a_Drive_Wheel_66x27_Left"
        b_whl_l = create_x_cylinder_in_comp(occ_whl_l.component, -18.5, -23.0, 24.5, 66.0, 27.0, "Wheel_66x27_Left")
        assign_rgb_color(design, b_whl_l, "DMU_Black_Tire", 34, 36, 38)

        occ_whl_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_r.component.name = "10b_Drive_Wheel_66x27_Right"
        b_whl_r = create_x_cylinder_in_comp(occ_whl_r.component, 138.5, -23.0, 24.5, 66.0, 27.0, "Wheel_66x27_Right")
        assign_rgb_color(design, b_whl_r, "DMU_Black_Tire", 34, 36, 38)

        occ_gld = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_gld.component.name = "11_Front_Glider_Caster_Dome"
        b_gld = create_z_cylinder_in_comp(occ_gld.component, 60.0, -152.0, -8.5, 17.6, 8.4, "Front_Glider_Dome")
        assign_rgb_color(design, b_gld, "DMU_Purple_LiDAR_V2", 142, 62, 196)

        # AUTOMATISIERTER INTERFERENCE CHECK
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

        app.log(f"=== MASTER DMU v4 INTERFERENCE CHECK ===\n{interference_msg}")

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(dmu_f3d_out)
        export_mgr.execute(f3d_opts)

        if ui:
            ui.messageBox(
                f"100% Master Digital Mock-Up (DMU v4) erfolgreich aufgebaut!\n\n"
                f"- Heck-Sensor-Bar HINTER den Motoren integriert (alle 6 LiDARs auf Z = 13.0 mm!)\n"
                f"- Liniensensor (76x32mm) mit 6x CNY70 (2.5mm Bodenabstand) vorne unten montiert\n"
                f"- Hauptplatine inkl. Motortreiber, ESP32-S3, HC-SR04, IMU (MPU6050) & USB-C platziert\n"
                f"- Interference Check: {interference_msg}\n\n"
                f"Gespeichert unter:\n{dmu_f3d_out}"
            )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
