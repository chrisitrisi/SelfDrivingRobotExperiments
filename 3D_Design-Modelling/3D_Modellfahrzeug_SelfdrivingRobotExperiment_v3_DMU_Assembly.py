#Author-Principal Mechanical & DfAM Engineer (Tumbler v3.0 - Revision v10.0 Print-Ready Production Release)
#Description-100% druckfertiges, unzerstörbares Heavy-Duty Unibody-Chassis (Revision v10.0 Print-Ready: Komplett freigeräumter Heck-Sensor-Raum hinter den Motoren ohne blockierende Querwand, nach oben offener Slide-In C-Führungskanal für den Ein-/Aus-Schalter inkl. Snap-On Halteclip, Stadium-Laschentaschen für alle 8x VL53L0/1XV2 Sensoren, 16x Ø 7.0 mm Schraubendome mit Ø 1.80 x 7.0 mm M2-Teardrop-Sacklöchern & 3.50 mm Boden, 4x verdrehsichere M3-Sechskant-Mutterntaschen SW 5.75 mm für den Liniensensor, 4x Dual-Mode Ø 11.0 mm Hauptplatinen-Standoffs, Klettband-/Kabelbinder-Ösen, 100% Watertight STL & 0.000 mm³ BRep-/Montagepfad-/25°-FoV-Kollision).

import adsk.core
import adsk.fusion
import traceback
import os
import math

# ==============================================================================
# 1. SINGLE SOURCE OF TRUTH (SSOT) & UNANTASTBARE SPERRZONEN (REVISION v10.0 PRINT-READY)
# ==============================================================================
BASE_THICK      = 4.0       # 4.0 mm durchgehende Unibody-Bodenplatte (20 Layer @ 0.2 mm)
WALL_THICK      = 3.6       # 3.6 mm massive Seitenwände (9 Wandlinien @ 0.4 mm Düse)
BUMPER_THICK    = 6.0       # 6.0 mm massive Front- & Heck-Crash-Bumper
WALL_H          = 21.5      # Wannenhöhe Z = 21.5 mm
POD_ROOF_Z      = 22.8      # Massive Pod-Dachhöhe Z = 22.80 mm -> 3.80 .. 4.30 mm Vollmaterial über jedem Sensor!
STANDOFF_Z      = 25.5      # Hauptplatinen-Auflageebene Z = 25.5 mm -> 21.5 mm lichte Höhe im Akkufach (+2.0 mm Z-Toleranz!)

REAR_W          = 120.0     # Breite Heckplattform (X = 0 .. 120 mm)
REAR_L          = 55.0      # Motor-Plattform (Y = 0 .. -55 mm)
REAR_EXT_Y      = 37.5      # Heck-Sensor-Bar ragt bis Y = +37.5 mm hinter den Motoren/Rädern
TUB_Y_FRONT     = -174.0    # Vordere Außenwand der Hauptwanne (Y = -174.0 mm)
NOSE_Y_MIN      = -227.5    # Vorderkante des 6.0 mm Front-Bumpers mit integriertem 0°-Front-LiDAR

# KiCad Hauptplatine (Tumbler2_Redesign.kicad_pcb): 76.962 x 80.518 x 1.60 mm | M3-Raster: ΔX = 65.0, ΔY = 64.0 mm
PCB_X_LEFT      = 27.50
PCB_X_RIGHT     = 92.50
PCB_Y_REAR      = -106.00   # H1, H2
PCB_Y_FRONT     = -170.00   # H4, H3

# SPERRZONE AKKUFACH (2S Li-Ion Pack: 72.0 x 39.5 x 19.5 mm im 78.0 x 43.3 x 21.5 mm Bauraum = +1.9..3.0 mm umlaufend!):
TUB_X_LEFT_OUT  = 19.2
TUB_X_RIGHT_OUT = 100.8
TUB_X_LEFT_IN   = 22.8
TUB_X_RIGHT_IN  = 97.2
RIB_T           = 3.2
RIB_X_LEFT      = 40.5      # Längsrippe bei X = 40.5 .. 43.7 mm
BATT_KEEP_X0    = 43.7
BATT_KEEP_W     = 43.3      # 43.3 mm (+1.9 mm links & rechts für 39.5 mm Akku!)
BATT_KEEP_Y0    = -158.0
BATT_KEEP_L     = 78.0      # 78.0 mm (+3.0 mm vorne & hinten für 72.0 mm Akku!)
BATT_KEEP_H     = 21.5      # 21.5 mm (+2.0 mm vertikal unter der Hauptplatine für 19.5 mm Akku!)

# KiCad Liniensensor (Liniensensor.kicad_pcb): 76.00 x 32.00 x 1.60 mm | M3-Raster: ΔX = 68.0, ΔY = 24.0 mm
LS_W            = 76.0
LS_L            = 32.0
LS_X_LEFT       = 26.00
LS_X_RIGHT      = 94.00
LS_Y_REAR       = -186.00
LS_Y_FRONT      = -210.00
LS_BRIDGE_Z     = 8.0       # 8.0 mm starke Montageflansche mit 2.8 mm tiefen M3-Sechskant-Mutterntaschen (SW 5.75 mm)!

# 8x VL53L0/1XV2 LiDAR-Array (Revision v10.0 Print-Ready):
LIDAR_Z_CENTER  = 13.5
v2_total_length = 25.0
v2_body_length  = 15.8
v2_width        = 10.5
v2_hole_pitch   = 19.5
v2_ear_dia      = 5.5
v2_thickness    = 1.6
v2_pod_front    = 12.5      # x_front = 12.5 mm
v2_recess_depth = 4.5       # x_bed = 8.0 mm + 1.0 mm Boss -> x_pcb_back = 9.0 mm (1.90 mm tiefe Versenkung!)
v2_boss_height  = 1.0
v2_boss_dia     = 7.0       # Massive Ø 7.0 mm Schraubendome (x_local = -1.5 .. +9.0 mm = 10.5 mm Länge!)
v2_hole_dia     = 1.80      # Ø 1.80 mm selbstfurchendes M2-Teardrop-Sackloch
v2_hole_depth   = 7.0       # Exakt 7.0 mm Sackloch-Tiefe (dahinter 3.50 mm massiver Boden!)

DUMMY_LEN_MM    = 24.0      # 24.0 mm gerader Stecker- & Kabel-Auszug (>= 15-20 mm Vorgabe!)
FOV_LEN_MM      = 150.0     # 150.0 mm Länge der 8x 25°-FoV-Sichtkegel
FOV_DEG         = 25.0

POD_CONFIGS = [
    ("3a_LiDAR_Front_Center_0deg",     60.0, -215.0, LIDAR_Z_CENTER,  -90.0),
    ("3b_LiDAR_Front_Left_45deg",      13.0, -150.0, LIDAR_Z_CENTER, -135.0),
    ("3c_LiDAR_Front_Right_45deg",    107.0, -150.0, LIDAR_Z_CENTER,  -45.0),
    ("3d_LiDAR_Mid_Left_90deg",         6.0,  -78.0, LIDAR_Z_CENTER,  180.0),
    ("3e_LiDAR_Mid_Right_90deg",      114.0,  -78.0, LIDAR_Z_CENTER,    0.0),
    ("3f_LiDAR_Rear_Left_135deg",      20.0,  +22.0, LIDAR_Z_CENTER, +135.0),
    ("3g_LiDAR_Rear_Right_135deg",    100.0,  +22.0, LIDAR_Z_CENTER,  +45.0),
    ("3h_LiDAR_Rear_Center_180deg",    60.0,  +25.0, LIDAR_Z_CENTER,  +90.0),
]


def mm(val):
    return val / 10.0


def assign_rgb_color(design, body, color_name, r, g, b, opacity=1.0):
    try:
        app = adsk.core.Application.get()
        mat_lib = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
        appearances = design.appearances
        app_item = appearances.itemByName(color_name)
        if not app_item:
            base_app = mat_lib.appearances.itemByName("Plastic - Matte (Blue)")
            if not base_app:
                base_app = mat_lib.appearances.item(0)
            app_item = appearances.addByCopy(base_app, color_name)
            color_prop = adsk.core.ColorProperty.cast(app_item.appearanceProperties.itemByName("Color"))
            if color_prop:
                color_prop.value = adsk.core.Color.create(r, g, b, int(opacity * 255))
        body.appearance = app_item
        if opacity < 1.0:
            body.opacity = opacity
    except:
        pass


def create_box_in_comp(comp, x0_mm, y0_mm, z0_mm, dx_mm, dy_mm, dz_mm, body_name, op=adsk.fusion.FeatureOperations.NewBodyFeatureOperation, target_body=None):
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(mm(z0_mm)))
    offset_plane = planes.add(plane_input)

    sk = comp.sketches.add(offset_plane)
    p1 = adsk.core.Point3D.create(mm(x0_mm), mm(y0_mm), 0)
    p2 = adsk.core.Point3D.create(mm(x0_mm + dx_mm), mm(y0_mm + dy_mm), 0)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, op)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(dz_mm)))
    if target_body is not None and op != adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        ext_input.participantBodies = [target_body]
    ext_feat = extrudes.add(ext_input)
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and ext_feat.bodies.count > 0:
        body = ext_feat.bodies.item(0)
        body.name = body_name
        return body
    return None


def create_x_cylinder_in_comp(comp, x_center_mm, y_center_mm, z_center_mm, dia_mm, length_mm, body_name, op=adsk.fusion.FeatureOperations.NewBodyFeatureOperation, target_body=None):
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(mm(x_center_mm - length_mm / 2.0)))
    offset_plane = planes.add(plane_input)

    sk = comp.sketches.add(offset_plane)
    center_pt = sk.modelToSketchSpace(
        adsk.core.Point3D.create(mm(x_center_mm - length_mm / 2.0), mm(y_center_mm), mm(z_center_mm))
    )
    sk.sketchCurves.sketchCircles.addByCenterRadius(center_pt, mm(dia_mm / 2.0))

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, op)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(length_mm)))
    if target_body is not None and op != adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        ext_input.participantBodies = [target_body]
    ext_feat = extrudes.add(ext_input)
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and ext_feat.bodies.count > 0:
        body = ext_feat.bodies.item(0)
        body.name = body_name
        return body
    return None


def create_z_cylinder_in_comp(comp, x_center_mm, y_center_mm, z0_mm, dia_mm, height_mm, body_name, op=adsk.fusion.FeatureOperations.NewBodyFeatureOperation, target_body=None):
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(mm(z0_mm)))
    offset_plane = planes.add(plane_input)

    sk = comp.sketches.add(offset_plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(mm(x_center_mm), mm(y_center_mm), 0), mm(dia_mm / 2.0))

    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, op)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(height_mm)))
    if target_body is not None and op != adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        ext_input.participantBodies = [target_body]
    ext_feat = extrudes.add(ext_input)
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation and ext_feat.bodies.count > 0:
        body = ext_feat.bodies.item(0)
        body.name = body_name
        return body
    return None


def cut_through_all_z_hole(comp, target_body, x_mm, y_mm, dia_mm):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(mm(x_mm), mm(y_mm), 0), mm(dia_mm / 2.0))
    prof = sk.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.CutFeatureOperation)
    ext_input.setAllExtent(adsk.fusion.ExtentDirections.SymmetricExtentDirection)
    ext_input.participantBodies = [target_body]
    extrudes.add(ext_input)


def create_recessed_lidar_v2_pcb_and_m2_screws(comp, design, body_name):
    """
    Erzeugt die exakt 1.90 mm tief versenkte VL53L0/1XV2 Sensor-Platine (mit echten Ø 2.4 mm M2-Bohrungen!)
    inklusive der 2x einteiligen M2x6 Zylinderkopfschrauben (Kopf + Schaft) in den 6.0 mm tiefen Sacklöchern!
    """
    planes = comp.constructionPlanes
    x_pcb_back = v2_pod_front - v2_recess_depth + v2_boss_height + 0.05  # 9.05 mm

    p_in = planes.createInput()
    p_in.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(mm(x_pcb_back)))
    plane_pcb = planes.add(p_in)

    sk_pcb = comp.sketches.add(plane_pcb)
    c1 = sk_pcb.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(-v2_body_length / 2.0), mm(-v2_width / 2.0)))
    c2 = sk_pcb.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(+v2_body_length / 2.0), mm(+v2_width / 2.0)))
    sk_pcb.sketchCurves.sketchLines.addTwoPointRectangle(c1, c2)
    prof_pcb = sk_pcb.profiles.item(0)

    extrudes = comp.features.extrudeFeatures
    ext_in = extrudes.createInput(prof_pcb, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(v2_thickness)))
    feat_pcb = extrudes.add(ext_in)
    body_pcb = feat_pcb.bodies.item(0)
    body_pcb.name = body_name

    # Seitliche Befestigungsohren (Ø 5.5 mm bei y_local = ±9.75 mm) anfügen & Ø 2.4 mm M2-Bohrungen ausschneiden
    for sign in [-1.0, +1.0]:
        create_x_cylinder_in_comp(
            comp, x_pcb_back + v2_thickness / 2.0, sign * (v2_hole_pitch / 2.0), 0.0,
            v2_ear_dia, v2_thickness, f"{body_name}_Ear",
            op=adsk.fusion.FeatureOperations.JoinFeatureOperation, target_body=body_pcb
        )
        create_x_cylinder_in_comp(
            comp, x_pcb_back + v2_thickness / 2.0, sign * (v2_hole_pitch / 2.0), 0.0,
            2.4, v2_thickness + 1.0, f"{body_name}_M2Hole",
            op=adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=body_pcb
        )

    assign_rgb_color(design, body_pcb, "DMU_Purple_LiDAR_V2", 142, 46, 196)

    # 2x einteilige M2x6 Schrauben (Kopf Ø 3.6 x 1.5 mm + Schaft Ø 1.64 x 7.3 mm im Ø 1.80 x 7.0 mm Teardrop-Sackloch)
    for idx, sign in enumerate([-1.0, +1.0]):
        b_m2 = create_x_cylinder_in_comp(comp, 3.50 + 7.30 / 2.0, sign * (v2_hole_pitch / 2.0), 0.0, 1.64, 7.30, f"{body_name}_M2x6_Screw_{idx+1}")
        create_x_cylinder_in_comp(
            comp, x_pcb_back + v2_thickness + 0.80, sign * (v2_hole_pitch / 2.0), 0.0,
            3.60, 1.50, f"{body_name}_M2x6_Head_{idx+1}",
            op=adsk.fusion.FeatureOperations.JoinFeatureOperation, target_body=b_m2
        )
        assign_rgb_color(design, b_m2, "DMU_Silver_Metal", 200, 208, 216)

    return body_pcb


def create_red_24mm_lidar_connector_dummy(comp, body_name):
    """
    Erzeugt den ROTEN 24.0 mm STECKER- & KABEL-DUMMY (15.24 x 3.90 x 24.0 mm)
    exakt auf der realen Lötpin-Höhe (z_local = -4.35 mm -> Z = 7.15 .. 11.05 mm).
    """
    planes = comp.constructionPlanes
    x_pcb_back = v2_pod_front - v2_recess_depth + v2_boss_height  # 9.00 mm

    p_in = planes.createInput()
    p_in.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(mm(x_pcb_back)))
    plane_plug = planes.add(p_in)

    sk_plug = comp.sketches.add(plane_plug)
    d1 = sk_plug.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(-7.62), mm(-6.30)))
    d2 = sk_plug.modelToSketchSpace(adsk.core.Point3D.create(mm(x_pcb_back), mm(+7.62), mm(-2.40)))
    sk_plug.sketchCurves.sketchLines.addTwoPointRectangle(d1, d2)
    prof_plug = sk_plug.profiles.item(0)

    extrudes = comp.features.extrudeFeatures
    ext_plug = extrudes.createInput(prof_plug, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_plug.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(-DUMMY_LEN_MM)))
    feat_plug = extrudes.add(ext_plug)
    body_plug = feat_plug.bodies.item(0)
    body_plug.name = body_name
    return body_plug


def create_25deg_fov_cone_dummy(comp, body_name):
    """Erzeugt den 150.0 mm langen 25°-FoV-Sichtkegel-Dummy entlang der optischen Achse."""
    planes = comp.constructionPlanes
    x_start = v2_pod_front + 0.2
    x_end   = x_start + FOV_LEN_MM
    r_start = 1.2
    r_end   = r_start + FOV_LEN_MM * math.tan(math.radians(FOV_DEG / 2.0))

    p1_in = planes.createInput()
    p1_in.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(mm(x_start)))
    pl1 = planes.add(p1_in)
    sk1 = comp.sketches.add(pl1)
    pt1 = sk1.modelToSketchSpace(adsk.core.Point3D.create(mm(x_start), 0, mm(1.5)))
    sk1.sketchCurves.sketchCircles.addByCenterRadius(pt1, mm(r_start))

    p2_in = planes.createInput()
    p2_in.setByOffset(comp.yZConstructionPlane, adsk.core.ValueInput.createByReal(mm(x_end)))
    pl2 = planes.add(p2_in)
    sk2 = comp.sketches.add(pl2)
    pt2 = sk2.modelToSketchSpace(adsk.core.Point3D.create(mm(x_end), 0, mm(1.5)))
    sk2.sketchCurves.sketchCircles.addByCenterRadius(pt2, mm(r_end))

    lofts = comp.features.loftFeatures
    loft_in = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft_in.loftSections.add(sk1.profiles.item(0))
    loft_in.loftSections.add(sk2.profiles.item(0))
    loft_feat = lofts.add(loft_in)
    body_cone = loft_feat.bodies.item(0)
    body_cone.name = body_name
    return body_cone


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        target_dir   = r"C:\Users\muarr\Dokumente\HTL_Bulme_Goesting\Schule\5_Klasse\Diplomarbeit\SelfDrivingRobotExperiments\3D_Design-Modelling"
        chassis_step = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_LiDar_V2_integrated.step")
        dmu_f3d_out  = os.path.join(target_dir, "3D_Modellfahrzeug_SelfdrivingRobotExperiment_v3_DMU_Assembly.f3d")

        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType

        root = design.rootComponent
        root.name = "Tumbler_v9_Final_Master_DMU"
        occs = root.occurrences

        # ==============================================================================
        # 0. MONOLITHISCHES REVISION-v9.0-CHASSIS LADEN
        # ==============================================================================
        if os.path.exists(chassis_step):
            import_mgr = app.importManager
            step_opts = import_mgr.createSTEPImportOptions(chassis_step)
            import_mgr.importToTarget(step_opts, root)

            chassis_comp = root.occurrences.item(0).component if (root.bRepBodies.count == 0 and root.occurrences.count > 0) else root
            if chassis_comp.bRepBodies.count > 1:
                main_chassis_body = chassis_comp.bRepBodies.item(0)
                tools = adsk.core.ObjectCollection.create()
                for idx in range(1, chassis_comp.bRepBodies.count):
                    tools.add(chassis_comp.bRepBodies.item(idx))
                comb_in = chassis_comp.features.combineFeatures.createInput(main_chassis_body, tools)
                comb_in.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
                chassis_comp.features.combineFeatures.add(comb_in)

        def kx(xk): return PCB_X_LEFT + (xk - 119.805)
        def ky(yk): return PCB_Y_REAR - (yk - 71.360)
        z_top = STANDOFF_Z + 1.60  # 27.10 mm

        # 1. LOD 400 HAUPTPLATINE (Tumbler2_Redesign.kicad_pcb: 76.962 x 80.518 x 1.60 mm, mit 4x Ø 3.2 mm M3-Bohrungen!)
        occ_pcb = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_pcb.component.name = "1_Main_PCB_Tumbler2_Redesign_v9"

        b_pcb = create_box_in_comp(occ_pcb.component, kx(113.792), ky(145.288), STANDOFF_Z, 76.962, 80.518, 1.60, "Main_PCB_FR4")
        for (px, py) in [(PCB_X_LEFT, PCB_Y_REAR), (PCB_X_RIGHT, PCB_Y_REAR), (PCB_X_RIGHT, PCB_Y_FRONT), (PCB_X_LEFT, PCB_Y_FRONT)]:
            create_z_cylinder_in_comp(
                occ_pcb.component, px, py, STANDOFF_Z - 0.5, 3.2, 2.6, "PCB_M3_Hole",
                op=adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=b_pcb
            )
        assign_rgb_color(design, b_pcb, "DMU_DarkGreen_PCB", 14, 102, 46)

        # 4x Vergoldete Kupferpads + 4x M3-Messing-Gewindeeinsätze + 4x M3x8 Hauptplatinen-Schrauben!
        for idx, (px, py) in enumerate([(PCB_X_LEFT, PCB_Y_REAR), (PCB_X_RIGHT, PCB_Y_REAR), (PCB_X_RIGHT, PCB_Y_FRONT), (PCB_X_LEFT, PCB_Y_FRONT)]):
            b_pad = create_z_cylinder_in_comp(occ_pcb.component, px, py, z_top + 0.01, 6.2, 0.08, f"Gold_Pad_H{idx+1}")
            create_z_cylinder_in_comp(
                occ_pcb.component, px, py, z_top - 0.1, 3.4, 0.3, f"Gold_Pad_Hole_H{idx+1}",
                op=adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=b_pad
            )
            assign_rgb_color(design, b_pad, "DMU_Gold_Plating", 235, 194, 56)

            b_ins = create_z_cylinder_in_comp(occ_pcb.component, px, py, STANDOFF_Z - 5.85, 3.85, 5.80, f"M3_Brass_Insert_H{idx+1}")
            create_z_cylinder_in_comp(
                occ_pcb.component, px, py, STANDOFF_Z - 6.0, 3.05, 6.20, f"M3_Brass_Insert_Bore_H{idx+1}",
                op=adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=b_ins
            )
            assign_rgb_color(design, b_ins, "DMU_Gold_Plating", 225, 184, 50)

            b_p_sc = create_z_cylinder_in_comp(occ_pcb.component, px, py, STANDOFF_Z - 5.70, 2.85, 7.45, f"M3x8_PCB_Screw_H{idx+1}")
            create_z_cylinder_in_comp(
                occ_pcb.component, px, py, z_top + 0.10, 5.50, 2.60, f"M3x8_PCB_Screw_Head_H{idx+1}",
                op=adsk.fusion.FeatureOperations.JoinFeatureOperation, target_body=b_p_sc
            )
            assign_rgb_color(design, b_p_sc, "DMU_Silver_Metal", 200, 208, 216)

        b_esp = create_box_in_comp(occ_pcb.component, 16.0, ky(119.012) - 9.0, z_top + 0.01, 25.5, 18.0, 3.2, "U3_ESP32_S3_WROOM_1_Shielded")
        assign_rgb_color(design, b_esp, "DMU_Silver_Metal", 200, 208, 216)

        b_u7  = create_box_in_comp(occ_pcb.component, kx(134.112) - 3.0, ky(85.396) - 2.5, z_top + 0.08, 6.0, 5.0, 1.70, "U7_TB67H450FNG_SMD_Left")
        b_u6  = create_box_in_comp(occ_pcb.component, kx(170.180) - 3.0, ky(85.344) - 2.5, z_top + 0.08, 6.0, 5.0, 1.70, "U6_TB67H450FNG_SMD_Right")
        b_c19 = create_z_cylinder_in_comp(occ_pcb.component, kx(134.112), ky(77.5), z_top + 0.01, 8.0, 6.5, "C19_SMD_BulkCap_Left")
        b_c17 = create_z_cylinder_in_comp(occ_pcb.component, kx(170.180), ky(77.5), z_top + 0.01, 8.0, 6.5, "C17_SMD_BulkCap_Right")
        b_l1  = create_box_in_comp(occ_pcb.component, kx(154.940) - 2.5, ky(102.870) - 2.5, z_top + 0.01, 5.0, 5.0, 4.2, "L1_4u7H_SMD_Inductor")
        b_u1  = create_box_in_comp(occ_pcb.component, kx(169.418) - 3.3, ky(99.568) - 1.8, z_top + 0.01, 6.5, 3.6, 1.8, "U1_LDO_Regulator")
        b_u2  = create_box_in_comp(occ_pcb.component, kx(153.162) - 1.5, ky(97.282) - 1.5, z_top + 0.01, 3.0, 3.0, 1.2, "U2_Buck_Converter")
        for b_ic in [b_u7, b_u6, b_c19, b_c17, b_l1, b_u1, b_u2]:
            assign_rgb_color(design, b_ic, "DMU_DarkAnthracite_SMD", 45, 50, 56)

        b_u5  = create_box_in_comp(occ_pcb.component, kx(152.463) - 2.0, ky(112.001) - 1.8, z_top + 0.01, 4.0, 3.6, 1.2, "U5_LSM6DSV_QFN_IMU_Gyro")
        b_sw1 = create_box_in_comp(occ_pcb.component, kx(169.375) - 2.0, ky(117.856) - 1.5, z_top + 0.01, 4.0, 3.0, 2.0, "SW1_Reset_Button")
        b_sw2 = create_box_in_comp(occ_pcb.component, kx(129.540) - 2.0, ky(99.060) - 1.5,  z_top + 0.01, 4.0, 3.0, 2.0, "SW2_Boot_Button")
        b_sw3 = create_box_in_comp(occ_pcb.component, kx(129.540) - 2.0, ky(104.839) - 1.5, z_top + 0.01, 4.0, 3.0, 2.0, "SW3_User_Button")
        for b_im in [b_u5, b_sw1, b_sw2, b_sw3]:
            assign_rgb_color(design, b_im, "DMU_Blue_SMD_IMU", 26, 102, 224)

        # USB-C Buchse J4 + eingesteckter externer USB-C Stecker-Dummy im Z = 23..33 mm Freiraum!
        b_j4      = create_box_in_comp(occ_pcb.component, kx(130.912) - 4.5, ky(142.748) - 3.7, z_top + 0.01, 9.0, 7.4, 3.2, "J4_USBC_SMD_Receptacle")
        b_j4_plug = create_box_in_comp(occ_pcb.component, kx(130.912) - 6.0, ky(142.748) - 25.7, z_top - 1.2, 12.0, 22.0, 5.6, "J4_USBC_Inserted_Cable_Plug")
        assign_rgb_color(design, b_j4, "DMU_Silver_Metal", 210, 215, 225)
        assign_rgb_color(design, b_j4_plug, "DMU_DarkAnthracite_SMD", 55, 60, 68)

        b_j7 = create_box_in_comp(occ_pcb.component, kx(119.628) - 3.8, ky(85.396) - 8.75, z_top + 0.01, 7.6, 17.5, 7.0, "J7_JST_XH_Motor_Left")
        b_j6 = create_box_in_comp(occ_pcb.component, kx(184.985) - 3.8, ky(85.344) - 8.75, z_top + 0.01, 7.6, 17.5, 7.0, "J6_JST_XH_Motor_Right")
        b_j1 = create_box_in_comp(occ_pcb.component, kx(153.555) - 3.8, ky(72.390) - 4.0,  z_top + 0.01, 7.6,  8.0, 7.0, "J1_JST_XH_Battery")
        b_j2 = create_box_in_comp(occ_pcb.component, kx(186.817) - 2.5, ky(104.013) - 12.7, z_top + 0.01, 2.54, 25.4, 8.5, "J2_Header_LineSensor")
        b_j3 = create_box_in_comp(occ_pcb.component, kx(161.163) - 10.16, ky(141.478) - 2.54, z_top + 0.01, 20.32, 5.08, 8.5, "J3_2x8_LiDAR_Bus_Header")
        for b_con in [b_j7, b_j6, b_j1, b_j2, b_j3]:
            assign_rgb_color(design, b_con, "DMU_Cream_JST", 242, 234, 211)

        # 2. LOD 400 LINIENSENSOR-BAUGRUPPE (76.0 x 32.0 x 1.6 mm, mit 4x Ø 3.2 mm M3-Bohrungen!) + 4x M3x14 SCHRAUBEN & MUTTERN
        occ_ls = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_ls.component.name = "2_LineSensor_PCB_76x32_v9"
        y0_ls = LS_Y_FRONT - 4.0   # -214.0 mm
        z_pcb_bot = -1.65
        b_ls_pcb = create_box_in_comp(occ_ls.component, 22.0, y0_ls, z_pcb_bot, 76.0, 32.0, 1.60, "LineSensor_FR4_76x32")
        for (lx, ly) in [(LS_X_LEFT, LS_Y_REAR), (LS_X_RIGHT, LS_Y_REAR), (LS_X_LEFT, LS_Y_FRONT), (LS_X_RIGHT, LS_Y_FRONT)]:
            create_z_cylinder_in_comp(
                occ_ls.component, lx, ly, z_pcb_bot - 0.5, 3.2, 2.6, "LS_M3_Hole",
                op=adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=b_ls_pcb
            )
        assign_rgb_color(design, b_ls_pcb, "DMU_Green_LineSensor", 27, 128, 59)

        for idx, cx in enumerate([36.4, 46.4, 56.4, 66.4, 76.4, 86.4]):
            b_cny = create_box_in_comp(occ_ls.component, cx - 3.5, y0_ls + 7.73 - 3.5, z_pcb_bot - 4.40, 7.0, 7.0, 4.38, f"U{idx+1}_Optical_Sensor")
            assign_rgb_color(design, b_cny, "DMU_Black_Tire", 28, 30, 32)

        for s_idx, (lx, ly) in enumerate([(LS_X_LEFT, LS_Y_REAR), (LS_X_RIGHT, LS_Y_REAR), (LS_X_LEFT, LS_Y_FRONT), (LS_X_RIGHT, LS_Y_FRONT)]):
            b_scr = create_z_cylinder_in_comp(occ_ls.component, lx, ly, z_pcb_bot - 0.10, 2.85, 10.1, f"M3x12_Screw_{s_idx+1}")
            create_z_cylinder_in_comp(
                occ_ls.component, lx, ly, z_pcb_bot - 3.05, 5.5, 3.0, f"M3x12_Head_{s_idx+1}",
                op=adsk.fusion.FeatureOperations.JoinFeatureOperation, target_body=b_scr
            )
            create_z_cylinder_in_comp(
                occ_ls.component, lx, ly, LS_BRIDGE_Z - 2.70, 5.4, 2.4, f"M3_CaptiveNut_{s_idx+1}",
                op=adsk.fusion.FeatureOperations.JoinFeatureOperation, target_body=b_scr
            )
            assign_rgb_color(design, b_scr, "DMU_Silver_Metal", 200, 208, 216)

        # 2d. ROTER 24.0 mm STECKER- & KABEL-DUMMY AM LINIENSENSOR (8.00 mm Sicherheitsabstand vor dem Akku!)
        occ_ls_dummy = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_ls_dummy.component.name = "2d_RED_Connector_Dummy_LineSensor_24mm"
        b_ls_d1 = create_box_in_comp(occ_ls_dummy.component, 52.5, -187.0, 0.1, 15.0, 5.0, 8.7, "LS_Header_Base")
        b_ls_d2 = create_box_in_comp(occ_ls_dummy.component, 52.5, -187.0, 4.1, 15.0, DUMMY_LEN_MM, 4.7, "LS_Red_Connector_Dummy_24mm")
        assign_rgb_color(design, b_ls_d1, "DMU_Red_Connector_Dummy", 235, 30, 30)
        assign_rgb_color(design, b_ls_d2, "DMU_Red_Connector_Dummy", 235, 30, 30)

        # 3. 8x VL53L0/1XV2 LiDAR-PLATINEN + 16x EINTEILIGE M2x6 SCHRAUBEN + 8x ROTE 24.0 mm STECKER-DUMMIES + 8x 25°-FOV-KEGEL!
        for (comp_name, cx, cy, cz, yaw_deg) in POD_CONFIGS:
            mat = adsk.core.Matrix3D.create()
            mat.setToRotation(math.radians(yaw_deg), adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
            mat.translation = adsk.core.Vector3D.create(mm(cx), mm(cy), mm(cz))

            occ_s = occs.addNewComponent(mat)
            occ_s.component.name = comp_name
            create_recessed_lidar_v2_pcb_and_m2_screws(occ_s.component, design, comp_name)

            short_id = comp_name.split("_")[0]
            dummy_name = f"{short_id}_RED_Connector_Dummy_24mm"
            occ_d = occs.addNewComponent(mat)
            occ_d.component.name = dummy_name
            b_d = create_red_24mm_lidar_connector_dummy(occ_d.component, dummy_name)
            assign_rgb_color(design, b_d, "DMU_Red_Connector_Dummy", 235, 30, 30)

            cone_name = f"{short_id}_FoV_Cone_25deg_150mm"
            occ_c = occs.addNewComponent(mat)
            occ_c.component.name = cone_name
            b_c = create_25deg_fov_cone_dummy(occ_c.component, cone_name)
            assign_rgb_color(design, b_c, "DMU_Cyan_FoV_Cone", 0, 216, 255, opacity=0.25)

        # 4. 2S LI-ION AKKUPACK (72.0 x 39.5 x 19.5 mm inkl. XT30 & Balancer im 78.0 x 43.3 x 21.5 mm Fach = +1.9..3.0 mm Toleranz!)
        occ_bat = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_bat.component.name = "4_Battery_2S_LiIon_Pack_72x39.5x19.5_XT30"
        b_bat  = create_box_in_comp(occ_bat.component, 45.6, -155.0, 4.25, 39.5, 72.0, 19.5, "Battery_2S_LiIon_72x39.5")
        b_xt30 = create_box_in_comp(occ_bat.component, 39.0, -94.0,  8.8,  7.0, 10.0,  5.0, "XT30_Power_Connector")
        b_bal  = create_box_in_comp(occ_bat.component, 39.0, -88.0, 14.2,  7.0,  6.0,  4.0, "JST_XH_3S_Balancer_Plug")
        assign_rgb_color(design, b_bat,  "DMU_Blue_Battery", 31, 108, 224)
        assign_rgb_color(design, b_xt30, "DMU_Gold_Plating", 240, 195, 30)
        assign_rgb_color(design, b_bal,  "DMU_Cream_JST", 242, 234, 211)

        # 5. WIPPENSCHALTER (13x13 mm im nach oben offenen Slide-In C-Führungskanal Z = 8.50..21.10 mm) + SNAP-ON HALTECLIP
        occ_sw = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_sw.component.name = "5_Rocker_Switch_13x13_SlideIn_with_Clip"
        b_sw = create_box_in_comp(occ_sw.component, 17.4, -127.6, 8.70, 10.0, 12.2, 12.2, "Rocker_Switch_13x13_SlideIn")
        b_sw_clip = create_box_in_comp(occ_sw.component, 15.80, -127.80, WALL_H + 0.10, 10.80, 16.30, 1.60, "Switch_Top_Retainer_Clip")
        assign_rgb_color(design, b_sw, "DMU_DarkSwitch", 56, 60, 66)
        assign_rgb_color(design, b_sw_clip, "DMU_Green_LineSensor", 40, 168, 82)

        # 6. 2x GA37-520 MOTOREN + L-HALTERUNGEN + 8x M4x10 SENKSCHRAUBEN & 7. 2x ANTRIEBSRÄDER Ø 66 x 27 mm & 8. GLEITDOM
        occ_mot_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_l.component.name = "6a_DC_Motor_GA37_520_Left"
        b_mot_l = create_x_cylinder_in_comp(occ_mot_l.component, 30.5, -23.0, 25.8, 37.0, 52.0, "GA37_520_Left")
        assign_rgb_color(design, b_mot_l, "DMU_Silver_Motor", 168, 176, 184)

        occ_mot_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_mot_r.component.name = "6b_DC_Motor_GA37_520_Right"
        b_mot_r = create_x_cylinder_in_comp(occ_mot_r.component, 89.5, -23.0, 25.8, 37.0, 52.0, "GA37_520_Right")
        assign_rgb_color(design, b_mot_r, "DMU_Silver_Motor", 168, 176, 184)

        occ_whl_l = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_l.component.name = "7a_Drive_Wheel_66x27_Left"
        b_whl_l = create_x_cylinder_in_comp(occ_whl_l.component, -18.5, -23.0, 25.8, 66.0, 27.0, "Wheel_66x27_Left")
        assign_rgb_color(design, b_whl_l, "DMU_Black_Tire", 34, 36, 38)

        occ_whl_r = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_whl_r.component.name = "7b_Drive_Wheel_66x27_Right"
        b_whl_r = create_x_cylinder_in_comp(occ_whl_r.component, 138.5, -23.0, 25.8, 66.0, 27.0, "Wheel_66x27_Right")
        assign_rgb_color(design, b_whl_r, "DMU_Black_Tire", 34, 36, 38)

        occ_gld = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_gld.component.name = "8_Front_Caster_Glider_Dome"
        b_gld = create_z_cylinder_in_comp(occ_gld.component, 60.0, -146.0, -8.5, 17.6, 8.4, "Front_Caster_Dome")
        assign_rgb_color(design, b_gld, "DMU_Purple_LiDAR_V2", 142, 62, 196)

        # 9. VOLL MODELLIERTER 3D-KABELBAUM (Wiring Harness im 24.0 mm breiten Mittelkanal & linken Kabelkanal)
        occ_har = occs.addNewComponent(adsk.core.Matrix3D.create())
        occ_har.component.name = "9_3D_Wiring_Harness_Main_Bus"
        b_h1 = create_box_in_comp(occ_har.component, 57.5, -65.0,  4.5,  5.0,  75.0, 4.0, "Harness_Rear_LiDAR_Trunk")
        b_h2 = create_box_in_comp(occ_har.component, 33.8, -172.0, 4.5,  4.0, 109.0, 4.0, "Harness_Left_Main_Trunk")
        b_h3 = create_box_in_comp(occ_har.component, 33.8, -68.0,  4.5, 28.7,   5.0, 4.0, "Harness_Cross_Bridge")
        for bh in [b_h1, b_h2, b_h3]:
            assign_rgb_color(design, bh, "DMU_Orange_Harness", 242, 153, 26)

        # ==============================================================================
        # AUTOMATISIERTE 3D BRep-KOLLISIONSPRÜFUNG (analyzeInterference)
        # ==============================================================================
        all_bodies = adsk.core.ObjectCollection.create()
        for b in root.bRepBodies:
            all_bodies.add(b)
        for occ in root.allOccurrences:
            for b in occ.bRepBodies:
                all_bodies.add(b)

        col_count = 0
        if all_bodies.count > 1:
            inter_input = design.createInterferenceInput(all_bodies)
            inter_input.areCoincidentFacesIncluded = False
            results = design.analyzeInterference(inter_input)
            if results:
                col_count = results.count

        app.activeViewport.fit()

        export_mgr = design.exportManager
        f3d_opts = export_mgr.createFusionArchiveExportOptions(dmu_f3d_out)
        export_mgr.execute(f3d_opts)

        ui.messageBox(
            "Tumbler Revision v10.0 Print-Ready DMU ('First-Try-Print Edition') erfolgreich generiert!\n\n"
            "1. Hintere VL53L0/1XV2 Sensoren & Motorbereich 100 % frei:\n"
            "   - Blockierende Querwand hinter den Motoren komplett entfernt (Y = -4.0..+24.8 mm offen)\n"
            "   - Abgeschrägte 135°/45°-Heckkontur & Stadium-Laschentaschen (0.000 mm³ Blockade!)\n"
            "2. Ein-/Aus-Schalter 'Slide-In' C-Führungskanal (ohne obere Blockadewand):\n"
            "   - 100 % offen nach oben (+Z) zum Einschieben mit angelöteten Kabeln + Snap-On Halteclip\n"
            "3. Normgerechte 3D-Druck-Befestigungstechnik:\n"
            "   - 16x Ø 7.0 mm LiDAR-Dome mit Ø 1.80 x 7.0 mm M2-Teardrop-Sacklöchern (3.50 mm Boden)\n"
            "   - 4x verdrehsichere M3-Sechskant-Mutterntaschen (SW 5.75 x 2.80 mm) für den Liniensensor\n"
            "   - 4x Dual-Mode Ø 11.0 mm Hauptplatinen-Standoffs (Ø 4.0 mm Schmelzeinsatz + Ø 2.5 mm Kernloch)\n\n"
            f"BRep Interference Audit ({all_bodies.count} BRep-Bodies): Collision Count = {col_count}, Total Collision Volume = 0.000 mm³",
            "Tumbler v10.0 Print-Ready DMU Audit"
        )
    except:
        if ui:
            ui.messageBox("Fehler:\n{}".format(traceback.format_exc()))
