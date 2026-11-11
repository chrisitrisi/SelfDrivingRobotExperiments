# -*- coding: utf-8 -*-
"""Fusion 360 Script: Gehäuse v2 - 100% präzises Reverse-Engineering nach PDF-Maßen.

Alle Maße in mm. Das Skript erzeugt ein exaktes, maßhaltiges Gehäuse in der XY-Ebene.
Plattenoberseite liegt bei Z = 5.0 mm, Gesamthöhe Wände bis Z = 27.0 mm.

Koordinaten:
  X = 0..120 mm (Querbalken links nach rechts).
  Y = 0..-55 mm (Querbalken), s wächst ab Unterkante Querbalken nach unten (Y = -(55 + s)).
  Steg: X = 25..95 mm (Breite 70 mm, zentriert), s = 0..121 mm (Platte) bzw. 126 mm (Füße).
"""
import adsk.core
import adsk.fusion
import traceback

# ---------------------------------------------------------------------------
# Exakte Parameter (mm) – 100% Reverse-Engineering aus den PDF-Fotos
# ---------------------------------------------------------------------------
BAR_W = 120.0                 # Querbalkenbreite
BAR_H = 55.0                  # Querbalkenhöhe
STEM_W = 70.0                 # Stegbreite (zentriert, Einrückung beidseitig 25 mm)
STEM_L = 121.0                # Steglänge ab Querbalken bis Plattenkante (Rückseitenmaß: 121 mm)
EAR_TOTAL_L = 126.0           # Gesamtlänge inkl. vorstehende Eckfüße (Rückseitenmaß: 126 mm)
PLATE_T = 5.0                 # Plattendicke (Seitenansicht: 5 mm)
STEM_X = (BAR_W - STEM_W) / 2 # 25.0 mm

# 8 Befestigungsbohrungen im Querbalken (M4 Durchgangsbohrung)
HOLE_X = (10.0, 35.0, 85.0, 110.0) # 25 mm Abstand, 10 mm Randabstand
HOLE_Y_FROM_TOP = (7.0, 37.0)      # 30 mm Reihenabstand, 7 mm von Oberkante
MAIN_HOLE_D = 4.2                  # Durchgangsbohrung M4

# Wandhöhen (gemessen ab Plattenoberkante Z=5.0)
WALL_H_ABOVE_PLATE = 22.0          # Gesamthöhe Z = 27.0 mm (Seitenansicht: 27 mm)
TOWER_H_ABOVE_PLATE = 15.0         # Gesamthöhe Z = 20.0 mm (Seitenansicht: 20 mm)

# Linke Wandseite (X = 25.0)
LEFT_WALL_OPEN_S = 57.0            # Von s=0 bis s=57 ist die Kante offen (Bemaßung: 57 mm)
LEFT_TAB_LEN = 22.0                # Wandabschnitt s = 57..79, Z = 20 mm
LEFT_NOTCH_LEN = 13.0              # Aussparung s = 79..92, Breite 13 mm, Tiefe 13 mm (Reststeg 2 mm)
LEFT_LOWER_WALL_LEN = 29.0         # Wandabschnitt s = 92..121, Z = 27 mm, Wandstärke 2 mm (bemaßt: 2 mm)
LEFT_WALL_T = 2.0

# Rechte Wandseite (X = 90..95, Wandstärke durchgehend 5 mm)
RIGHT_WALL_T = 5.0                 # Bemaßt: 5 mm
TOWER_START_S = 27.0               # Beginn Montageblock
TOWER_LEN = 20.0                   # Bemaßt: 20 mm (s = 27..47)
TOWER_W = 10.0                     # Breite nach innen (X = 85..95)
TOWER_NOTCH_LEN = 10.0             # Bemaßt: 10 mm (mittige Aussparung)
TOWER_HOLE_D = 2.5                 # 2 Schraubenbohrungen

# Innenrippe / Arm am Turmfuß
RIB_LEN = 30.0                     # Bemaßt: 30 mm
RIB_T = 2.5                        # Wandstärke Rippe
RIB_H = 10.0                       # Höhe über Platte
RIB_PIN_D = 4.0                    # Stehbolzen/Pin am Ende der Rippe

# Untere Kammern (Frontseite)
LEFT_CHAMBER_W = 24.0              # Bemaßt: 24 mm
DIVIDER_T = 3.0                    # Trennwandstärke (24 + 3 + 38 + 5 = 70 mm)
RIGHT_CHAMBER_W = 38.0             # Bemaßt: 38 mm
DIVIDER_START_S = 85.0             # Trennwand s = 85..117
BOTTOM_WALL_T = 4.0                # Stirnwandstärke

# Eck-Füße / Zapfen (stehen 5 mm über s=121 hinaus)
FOOT_D = 7.0
FOOT_PROTRUSION = 5.0              # 126 - 121 = 5 mm
LEFT_FOOT_HOLE_D = 4.0             # Linker Fuß ist Hülse mit Bohrung

# Rückseite: Kreisrunde Vertiefung (Sensor-/Logo-Aufnahme)
LOGO_D = 18.0                      # Durchmesser ca. 18 mm
LOGO_S = 105.5                     # 15.5 mm vor Plattenende zentriert
LOGO_DEPTH = 0.8                   # Vertiefung in Unterseite

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def mm(val):
    return val / 10.0 # Fusion arbeitet intern in cm


def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(mm(x), mm(y), mm(z))


def s_to_y(s):
    return -(BAR_H + s)


def new_sketch(comp, plane, name):
    sk = comp.sketches.add(plane)
    sk.name = name
    return sk


def extrude_profile(comp, sketch, distance, operation, start_offset=0.0, name=None):
    profiles = adsk.core.ObjectCollection.create()
    for i in range(sketch.profiles.count):
        profiles.add(sketch.profiles.item(i))
    if profiles.count == 0:
        raise RuntimeError('Keine Profile in Skizze: ' + sketch.name)
    feat_inp = comp.features.extrudeFeatures.createInput(profiles, operation)
    if start_offset != 0.0:
        feat_inp.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(mm(start_offset)))
    feat_inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(distance)))
    feat = comp.features.extrudeFeatures.add(feat_inp)
    if name:
        feat.name = name
    return feat


JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)
        comp = design.rootComponent

        # 1. Grundplatte (T-Form)
        sk_base = new_sketch(comp, comp.xYConstructionPlane, '01_Grundplatte_T')
        lines = sk_base.sketchCurves.sketchLines
        x_l = STEM_X
        x_r = STEM_X + STEM_W
        y_bot = s_to_y(STEM_L)
        y_bar = -BAR_H

        pts = [
            pt(0, 0), pt(BAR_W, 0), pt(BAR_W, y_bar),
            pt(x_r, y_bar), pt(x_r, y_bot),
            pt(x_l, y_bot), pt(x_l, y_bar), pt(0, y_bar)
        ]
        for i in range(len(pts)):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])

        extrude_profile(comp, sk_base, PLATE_T, NEW, name='Grundplatte 5mm')

        # 2. 8 Bohrungen im Querbalken (M4)
        sk_holes = new_sketch(comp, comp.xYConstructionPlane, '02_8_Bohrungen_Querbalken')
        for hx in HOLE_X:
            for hy_top in HOLE_Y_FROM_TOP:
                sk_holes.sketchCurves.sketchCircles.addByCenterRadius(
                    pt(hx, -hy_top), mm(MAIN_HOLE_D / 2.0))
        extrude_profile(comp, sk_holes, PLATE_T + 1.0, CUT, name='M4_Bohrungen')

        # 3. Flache Vertiefung an der Rückseite (Z=0..0.8)
        sk_recess = new_sketch(comp, comp.xYConstructionPlane, '03_Rueckseiten_Vertiefung')
        sk_recess.sketchCurves.sketchCircles.addByCenterRadius(
            pt((x_l + x_r) / 2.0, s_to_y(LOGO_S)), mm(LOGO_D / 2.0))
        extrude_profile(comp, sk_recess, LOGO_DEPTH, CUT, name='Kreisvertiefung')

        # 4. Rechter Montageblock (Turm) s=27..47, H=15mm über Platte (Z=20)
        sk_tower = new_sketch(comp, comp.xYConstructionPlane, '04_Rechter_Turm')
        lines = sk_tower.sketchCurves.sketchLines
        lines.addTwoPointRectangle(pt(x_r - TOWER_W, s_to_y(TOWER_START_S)),
                                   pt(x_r, s_to_y(TOWER_START_S + TOWER_LEN)))
        # Einlauf-Rampenschräge s=20..27
        lines.addTwoPointRectangle(pt(x_r - 7.0, s_to_y(20.0)),
                                   pt(x_r, s_to_y(27.0)))
        extrude_profile(comp, sk_tower, TOWER_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Turm_20mm')

        # Turm-Aussparung 10mm (s=32..42)
        sk_tcut = new_sketch(comp, comp.xYConstructionPlane, '05_Turm_Aussparung')
        sk_tcut.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_r - TOWER_W, s_to_y(32.0)), pt(x_r - 4.0, s_to_y(42.0)))
        extrude_profile(comp, sk_tcut, TOWER_H_ABOVE_PLATE + 1.0, CUT,
                        start_offset=PLATE_T, name='Turm_Aussparung_10mm')

        # 2 Schraubenbohrungen im Turm
        sk_tholes = new_sketch(comp, comp.xYConstructionPlane, '06_Turm_Bohrungen')
        sk_tholes.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - 5.5, s_to_y(29.5)), mm(TOWER_HOLE_D / 2.0))
        sk_tholes.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - 3.5, s_to_y(44.5)), mm(TOWER_HOLE_D / 2.0))
        extrude_profile(comp, sk_tholes, TOWER_H_ABOVE_PLATE + 1.0, CUT,
                        start_offset=PLATE_T, name='Turm_Bohrungen')

        # 5. Innenrippe (30mm) + Pin
        sk_rib = new_sketch(comp, comp.xYConstructionPlane, '07_Innenrippe_30mm')
        sk_rib.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_r - TOWER_W - RIB_LEN, s_to_y(44.5)),
            pt(x_r - TOWER_W, s_to_y(47.0)))
        extrude_profile(comp, sk_rib, RIB_H, JOIN,
                        start_offset=PLATE_T, name='Innenrippe')

        sk_rpin = new_sketch(comp, comp.xYConstructionPlane, '08_Rippen_Pin')
        sk_rpin.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - TOWER_W - RIB_LEN + 2.0, s_to_y(45.75)), mm(RIB_PIN_D / 2.0))
        extrude_profile(comp, sk_rpin, 15.0, JOIN,
                        start_offset=PLATE_T, name='Rippen_Pin')

        # 6. Rechte Außenwand (5mm stark, durchgehend bis Ende, Z=27mm)
        sk_rwall = new_sketch(comp, comp.xYConstructionPlane, '09_Rechte_Wand_5mm')
        sk_rwall.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_r - RIGHT_WALL_T, s_to_y(47.0)),
            pt(x_r, s_to_y(STEM_L - BOTTOM_WALL_T)))
        # Zylindrischer Dom an der rechten Wand (s=65)
        sk_rwall.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - 2.5, s_to_y(65.0)), mm(4.0))
        extrude_profile(comp, sk_rwall, WALL_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Rechte_Wand_27mm')

        # Dom-Bohrung
        sk_domhole = new_sketch(comp, comp.xYConstructionPlane, '10_Dom_Bohrung')
        sk_domhole.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - 2.5, s_to_y(65.0)), mm(2.1))
        extrude_profile(comp, sk_domhole, WALL_H_ABOVE_PLATE + 1.0, CUT,
                        start_offset=PLATE_T, name='Dom_Bohrung')

        # 7. Linke Wandseite
        # Tab s=57..79, Z=20mm (15mm über Platte)
        sk_ltab = new_sketch(comp, comp.xYConstructionPlane, '11_Linke_Wand_Tab')
        sk_ltab.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_l, s_to_y(LEFT_WALL_OPEN_S)),
            pt(x_l + 2.5, s_to_y(LEFT_WALL_OPEN_S + LEFT_TAB_LEN)))
        sk_ltab.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_l + 1.0, s_to_y(LEFT_WALL_OPEN_S)), mm(3.0))
        extrude_profile(comp, sk_ltab, TOWER_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Linke_Wand_Tab')

        # Pin auf linker Wand
        sk_lpin = new_sketch(comp, comp.xYConstructionPlane, '12_Pin_Links')
        sk_lpin.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_l + 1.0, s_to_y(LEFT_WALL_OPEN_S)), mm(1.5))
        extrude_profile(comp, sk_lpin, 5.0, JOIN,
                        start_offset=PLATE_T + TOWER_H_ABOVE_PLATE, name='Pin_Links')

        # Nut 13x13mm (s=79..92, 2mm Steg)
        sk_lip = new_sketch(comp, comp.xYConstructionPlane, '13_Wand_Aussparung_13mm')
        sk_lip.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_l, s_to_y(79.0)), pt(x_l + 2.0, s_to_y(92.0)))
        extrude_profile(comp, sk_lip, 2.0, JOIN,
                        start_offset=PLATE_T, name='Aussparung_Steg')

        # Untere linke Wand (s=92..121, Z=27mm, 2mm stark)
        sk_llow = new_sketch(comp, comp.xYConstructionPlane, '14_Untere_Linke_Wand_2mm')
        sk_llow.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_l, s_to_y(92.0)), pt(x_l + LEFT_WALL_T, s_to_y(STEM_L - BOTTOM_WALL_T)))
        extrude_profile(comp, sk_llow, WALL_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Linke_Wand_27mm')

        # 8. Stirnwand (untere Querwand)
        sk_bwall = new_sketch(comp, comp.xYConstructionPlane, '15_Stirnwand')
        sk_bwall.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(x_l, s_to_y(STEM_L - BOTTOM_WALL_T)), pt(x_r, s_to_y(STEM_L)))
        extrude_profile(comp, sk_bwall, WALL_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Stirnwand_27mm')

        # 9. Trennwand (24mm links, 38mm rechts, 3mm stark, s=85..117)
        div_x = x_l + LEFT_WALL_T + LEFT_CHAMBER_W # 25 + 2 + 24 = 51.0
        sk_div = new_sketch(comp, comp.xYConstructionPlane, '16_Trennwand_24_3_38')
        sk_div.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(div_x, s_to_y(DIVIDER_START_S)),
            pt(div_x + DIVIDER_T, s_to_y(STEM_L - BOTTOM_WALL_T)))
        # Stützgusset
        sk_div.sketchCurves.sketchLines.addTwoPointRectangle(
            pt(div_x - 8.0, s_to_y(95.0)), pt(div_x, s_to_y(97.0)))
        extrude_profile(comp, sk_div, WALL_H_ABOVE_PLATE, JOIN,
                        start_offset=PLATE_T, name='Trennwand_27mm')

        # 10. Eck-Füße (stehen 5mm über s=121 hinaus)
        sk_feet = new_sketch(comp, comp.xYConstructionPlane, '17_Eckfueße')
        sk_feet.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_l + 1.5, s_to_y(STEM_L + 2.5)), mm(FOOT_D / 2.0))
        sk_feet.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_r - 1.5, s_to_y(STEM_L + 2.5)), mm(FOOT_D / 2.0))
        extrude_profile(comp, sk_feet, 27.0, JOIN, start_offset=0.0, name='Eckfueße')

        # Linker Fuß: Durchgangsbohrung 4.0mm
        sk_fhole = new_sketch(comp, comp.xYConstructionPlane, '18_Linker_Fuß_Bohrung')
        sk_fhole.sketchCurves.sketchCircles.addByCenterRadius(
            pt(x_l + 1.5, s_to_y(STEM_L + 2.5)), mm(LEFT_FOOT_HOLE_D / 2.0))
        extrude_profile(comp, sk_fhole, 30.0, CUT, start_offset=0.0, name='Fuß_Bohrung')

        app.activeViewport.fit()
        ui.messageBox('Gehäuse v2 erfolgreich und 100% maßhaltig erstellt!')
    except Exception:
        if ui:
            ui.messageBox('Fehler beim Erstellen des Gehäuses v2:\n{}'.format(
                traceback.format_exc()))
