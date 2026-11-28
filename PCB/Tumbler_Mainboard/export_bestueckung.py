"""Exportiere die JLC-Bestückungsdaten aus den beiden nativen KiCad-Varianten."""
import csv
import math
import os
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Fertigung"
PCB = ROOT / "Tumbler2_Redesign.kicad_pcb"
SCH = PCB.with_suffix(".kicad_sch")
BRIDGES = {"R87", "R88", "R89", "R92"}
HAND = ("J1", "J3", "J5", "SW4")
# Lokale Körpermitten in kartesischen mm bei KiCad-Drehung 0.
# J4: Metallgehäuse, ohne Hilfslinie zur Platinenkante und Pin-1-Markierung.
CENTERS = {
    "KINGHELM_KH-TYPE-C-16P": (0, 1.155),
    "JST_XH_S6B-XH-SM4-TB_1x06-1MP_P2.50mm_Horizontal": (0, -1.8),
    "JST_GH_BM10B-GHS-TBT_1x10-1MP_P1.25mm_Vertical": (0, 0.375),
}


def export(*args):
    subprocess.run([os.environ.get("KICAD_CLI", "kicad-cli"), *args], check=True)


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, headings, data):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headings)
        writer.writerows(data)


def rotation_offset(package):
    if package.startswith(("SOIC-", "SSOP-", "TSSOP-", "Texas_RGE0024H_")):
        return 270
    if package.startswith(("SOT-", "TSOT-")) or package in ("D_SMB", "CP_Elec_10x10"):
        return 180
    return 0


def write_pair(suffix, positions, components):
    groups = defaultdict(list)
    placements = []
    for pos in sorted(positions, key=lambda row: row["Ref"]):
        ref = pos["Ref"]
        part = components[ref]
        code, package = part["LCSC PN"], pos["Package"]
        if not code.startswith("C") or not code[1:].isdigit():
            raise ValueError(f"{ref}: fehlende LCSC-Nummer")
        groups[(part["Value"], package, code)].append(ref)
        rot = float(pos["Rot"])
        dx, dy = CENTERS.get(package, (0, 0))
        if pos["Side"] == "bottom" and (dx or dy):
            raise ValueError(f"{ref}: Mittelpunktkorrektur auf der Unterseite prüfen")
        a = math.radians(rot)
        x = float(pos["PosX"]) + dx * math.cos(a) - dy * math.sin(a)
        y = float(pos["PosY"]) + dx * math.sin(a) + dy * math.cos(a)
        placements.append((ref, f"{x:.4f}mm", f"{y:.4f}mm",
                           pos["Side"].title(), (rot + rotation_offset(package)) % 360))
    write(OUT / f"BOM_JLC{suffix}.csv", ("Comment", "Designator", "Footprint", "LCSC Part #"),
          ((v, ",".join(refs), fp, code) for (v, fp, code), refs in sorted(groups.items())))
    write(OUT / f"CPL_JLC{suffix}.csv", ("Designator", "Mid X", "Mid Y", "Layer", "Rotation"), placements)


def main():
    fields = "Reference,Value,Footprint,LCSC PN"
    export("sch", "export", "bom", "--fields", fields+",${QUANTITY},${DNP}",
           "--labels", fields+",QUANTITY,DNP", "--group-by", "Value,Footprint,LCSC PN,${DNP}",
           "-o", OUT / "BOM_KiCad.csv", SCH)
    export("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--exclude-dnp",
           "-o", OUT / "Positionen_KiCad.csv", PCB)
    variants = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, options in (("3S", []), ("2S", ["--variant", "2S"])):
            bom, pos = Path(tmp) / "bom.csv", Path(tmp) / "pos.csv"
            export("sch", "export", "bom", *options, "--fields", fields, "--exclude-dnp", "-o", bom, SCH)
            export("pcb", "export", "pos", *options, "--smd-only", "--exclude-dnp",
                   "--format", "csv", "--units", "mm", "-o", pos, PCB)
            parts = {r["Reference"]: r for r in rows(bom)}
            positions = rows(pos)
            refs = {r["Ref"] for r in positions}
            if len(refs) != len(positions) or refs != {r for r,p in parts.items() if p["LCSC PN"]} - set(HAND):
                raise ValueError(f"{name}: Schaltplan und Bestückungspositionen weichen voneinander ab")
            variants[name] = parts, positions, refs
    parts, positions, refs = variants["3S"]
    if variants["2S"][2] != refs | BRIDGES or refs & BRIDGES:
        raise ValueError("Die 2S/3S-Brücken stimmen nicht mit den KiCad-Varianten überein")
    write_pair("_beidseitig", positions, parts)
    write_pair("_2S_beidseitig", variants["2S"][1], variants["2S"][0])
    write_pair("", [p for p in positions if p["Side"] == "top"], parts)
    hand = [(ref, parts[ref]["Value"], parts[ref]["Footprint"].split(":")[-1],
             "Top", parts[ref]["LCSC PN"], "THT, beide Varianten") for ref in HAND]
    for pos in sorted(variants["2S"][1], key=lambda r:r["Ref"]):
        if pos["Side"] == "bottom":
            ref = pos["Ref"]
            reason = "Nur 2S; bei 3S frei lassen" if ref in BRIDGES else "Beide Varianten"
            part = variants["2S"][0][ref]
            hand.append((ref, part["Value"], pos["Package"], "Bottom", part["LCSC PN"],
                         f"{reason} (Handarbeit nur bei einseitiger Bestellung)"))
    write(OUT / "Selbst_bestuecken.csv", ("Referenz","Wert","Footprint","Seite","LCSC (zum Mitbestellen)","Grund"), hand)


if __name__ == "__main__":
    main()
