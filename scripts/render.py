#!/usr/bin/env python3
"""Regenerate the STLs, renders and diagrams from the OpenSCAD sources.

    python scripts/render.py                 # everything
    python scripts/render.py stl             # only the STLs in stl/
    python scripts/render.py png svg         # only the OpenSCAD renders and the paper template
    python scripts/render.py diagrams        # only the composed scenes and labelled diagrams

Targets:
    stl       printable parts -> stl/*.stl (binary)
    png       OpenSCAD renders of single parts -> docs/img/*.png
    svg       1:1 paper template of the cat face mask rim -> docs/cat_face_rim_template.svg
    diagrams  scenes composed from the exported STLs (print layout, assembled system) and the
              labelled sections drawn with matplotlib -> docs/img/*.png

Needs OpenSCAD 2021.01 or newer (found on PATH, in the default install location, or set
OPENSCAD / --openscad). The matplotlib diagrams also need the packages in
scripts/requirements.txt; without them that step is skipped with a warning.
PNG export uses OpenGL; on a headless Linux box run it under xvfb-run.
"""
import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAD = ROOT / "scad"
STL = ROOT / "stl"
DOCS = ROOT / "docs"
IMG = DOCS / "img"

MASK = "cat_face_inhaler_mask.scad"
ROUND = "round_cushion_inhaler_mask.scad"
CHAMBER = "holding_chamber.scad"

# output name, source file, parameter overrides (the round mask is first because it takes longest)
STLS = [
    ("round_cushion_inhaler_mask", ROUND, {}),
    ("cat_face_inhaler_mask", MASK, {}),
    ("holding_chamber_body", CHAMBER, {"part": "body"}),
    ("holding_chamber_cap", CHAMBER, {"part": "cap"}),
    ("holding_chamber_valve_insert", CHAMBER, {"part": "insert"}),
    ("holding_chamber_valve_flap", CHAMBER, {"part": "flap"}),
    ("holding_chamber_umbrella", CHAMBER, {"part": "umbrella"}),
    ("holding_chamber_one_piece_spacer", CHAMBER, {"part": "body", "one_piece": True, "valve": False}),
]

# output name, source file, camera rotation about X and Z in degrees, parameter overrides
PNGS = [
    ("round_mask_iso", ROUND, (60, 35), {}),
    ("round_mask_top", ROUND, (0, 0), {}),
    ("round_mask_section", ROUND, (90, 180), {"show_section": True}),
    ("cat_face_mask_iso", MASK, (60, 35), {}),
    ("cat_face_mask_top", MASK, (0, 0), {}),
    ("cat_face_mask_side", MASK, (90, 90), {}),
    ("cat_face_mask_section", MASK, (90, 180), {"show_section": True}),
    ("cat_face_rim_template_preview", MASK, (0, 0), {"part": "template"}),
    ("chamber_all_parts", CHAMBER, (55, 25), {}),
    ("chamber_body_iso", CHAMBER, (65, 30), {"part": "body"}),
    ("chamber_cap_iso", CHAMBER, (65, 30), {"part": "cap"}),
    ("chamber_cap_top", CHAMBER, (20, 25), {"part": "cap"}),
    ("chamber_cap_below", CHAMBER, (125, 30), {"part": "cap"}),
    ("chamber_valve_insert", CHAMBER, (35, 25), {"part": "insert"}),
    ("chamber_valve_flap", CHAMBER, (35, 25), {"part": "flap"}),
    ("chamber_umbrella", CHAMBER, (35, 25), {"part": "umbrella"}),
    ("chamber_assembly", CHAMBER, (70, 30), {"part": "assembly"}),
    ("chamber_assembly_section", CHAMBER, (90, 180), {"part": "assembly", "show_section": True}),
    ("chamber_exploded", CHAMBER, (75, 30), {"part": "exploded"}),
    ("chamber_one_piece", CHAMBER, (65, 30), {"part": "body", "one_piece": True, "valve": False}),
]

PNG_OPTS = ["--imgsize=1400,1050", "--viewall", "--autocenter", "--projection=p", "--colorscheme=Tomorrow"]

# holding_chamber.scad variables the diagrams are dimensioned from
CHAMBER_VARS = [
    "mouth_w", "mouth_h", "mouth_corner_r", "socket_taper", "socket_taper_depth", "socket_depth", "chamber_d", "chamber_len",
    "wall", "nozzle_len", "valve_d", "grille_w", "insert_t", "flap_t", "flap_overlap", "tab_w",
    "insert_clearance", "umbrella_d", "umbrella_t", "exhale_holes", "exhale_hole_d", "pocket_depth",
    "ma", "mb", "Ri", "z_sock", "z_cone", "z_top", "na", "nb", "nt", "skirt_h", "skirt_od", "bore_d",
    "z_c", "z_n", "z_lid", "cap_h", "flap_d", "hinge_r", "slot_w", "slot_t", "pocket_d", "r_ex", "seat_z",
    "seat_t", "bulb_pocket_h", "lid_d", "ex_on",
]

TPU_COLOR = "#e0a526"     # masks, flap, umbrella
RIGID_COLOR = "#3f73b8"   # chamber body, cap, insert
INHALER_COLOR = "#9a9aa2"


def find_openscad(explicit=None):
    candidates = [explicit, os.environ.get("OPENSCAD")]
    if os.name == "nt":
        # openscad.com is the console build: it reports errors to the terminal, openscad.exe does not
        candidates += [shutil.which("openscad.com")]
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", "")):
            candidates += [os.path.join(base, d, "openscad.com") for d in ("OpenSCAD", "OpenSCAD (Nightly)")]
    candidates += [shutil.which("openscad"), "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    sys.exit("OpenSCAD not found: install it, put it on PATH, or pass --openscad / set OPENSCAD")


def scad_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return json.dumps(v)
    return repr(v)


def run_openscad(openscad, out, src, params=None, extra=()):
    """Run one export; returns (seconds, warning/error lines). Raises RuntimeError on failure."""
    cmd = [openscad, "-o", str(out), *extra]
    for k, v in (params or {}).items():
        cmd += ["-D", f"{k}={scad_value(v)}"]
    cmd.append(str(src))
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (res.stdout + res.stderr).splitlines()
    issues = [line.strip() for line in log if "WARNING" in line or "ERROR" in line]
    if res.returncode != 0 or not Path(out).is_file():
        raise RuntimeError("\n".join(issues or log[-10:]) or f"exit code {res.returncode}")
    return time.time() - t0, issues


def stl_job(openscad, name, src, params):
    return run_openscad(openscad, STL / f"{name}.stl", SCAD / src, params, ["--export-format", "binstl"])


def png_job(openscad, out, src, rot, params, distance=300):
    camera = f"--camera=0,0,0,{rot[0]},0,{rot[1]},{distance}"
    return run_openscad(openscad, out, src, params, PNG_OPTS + [camera])


def run_jobs(jobs, workers):
    """jobs: list of (label, callable). Prints one line per job; returns the number of failures."""
    failures = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [(label, pool.submit(fn)) for label, fn in jobs]
        for label, fut in futures:
            try:
                secs, issues = fut.result()
                print(f"  {label:<44} {secs:6.1f} s")
                for line in issues:
                    print(f"      {line}")
            except RuntimeError as e:
                failures += 1
                print(f"  {label:<44} FAILED")
                for line in str(e).splitlines():
                    print(f"      {line}")
    return failures


def scad_path(p):
    return Path(p).resolve().as_posix()


def chamber_params(openscad):
    """Evaluate holding_chamber.scad and return its derived dimensions as a dict."""
    with tempfile.TemporaryDirectory() as tmp:
        wrapper = Path(tmp) / "params.scad"
        pairs = ", ".join(f'["{v}", {v}]' for v in CHAMBER_VARS)
        wrapper.write_text(f"include <{scad_path(SCAD / CHAMBER)}>\necho(DIAGRAM_PARAMS = [{pairs}]);\n", encoding="utf-8")
        out = Path(tmp) / "params.echo"
        run_openscad(openscad, out, wrapper)
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.startswith("ECHO: DIAGRAM_PARAMS = "):
                return dict(json.loads(line.split(" = ", 1)[1]))
    raise RuntimeError("could not read the chamber parameters")


def stl_bounds(path):
    """(min xyz, max xyz) of a binary STL."""
    data = Path(path).read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + 50 * n:
        raise RuntimeError(f"{path} is not a binary STL: run the stl target first")
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    for i in range(n):
        v = struct.unpack_from("<9f", data, 84 + 50 * i + 12)
        for k in range(9):
            lo[k % 3] = min(lo[k % 3], v[k])
            hi[k % 3] = max(hi[k % 3], v[k])
    return lo, hi


def scene_job(openscad, name, scad_text, rot, distance):
    def job():
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / f"{name}.scad"
            src.write_text(scad_text, encoding="utf-8")
            return png_job(openscad, IMG / f"{name}.png", src, rot, {}, distance)
    return job


def print_layout_scene():
    """Every printable part as exported, in print orientation, coloured by material."""
    big = [("holding_chamber_body", RIGID_COLOR), ("holding_chamber_cap", RIGID_COLOR),
           ("cat_face_inhaler_mask", TPU_COLOR), ("round_cushion_inhaler_mask", TPU_COLOR)]
    small = [("holding_chamber_valve_insert", RIGID_COLOR), ("holding_chamber_valve_flap", TPU_COLOR),
             ("holding_chamber_umbrella", TPU_COLOR)]
    gap = 10
    lines, x = [], 0.0
    for name, color in big:
        lo, hi = stl_bounds(STL / f"{name}.stl")
        cx, cy = x - lo[0], -(lo[1] + hi[1]) / 2
        lines.append(f'color("{color}") translate([{cx:.2f}, {cy:.2f}, {-lo[2]:.2f}]) import("{scad_path(STL / name)}.stl");')
        x += hi[0] - lo[0] + gap
    # small parts in a column in front of the body
    y = None
    for name, color in small:
        lo, hi = stl_bounds(STL / f"{name}.stl")
        if y is None:
            y = -max(20.0, (hi[1] - lo[1]) / 2) - gap
        cx, cy = -lo[0] - (hi[0] - lo[0]) - gap, y - hi[1]
        lines.append(f'color("{color}") translate([{cx:.2f}, {cy:.2f}, {-lo[2]:.2f}]) import("{scad_path(STL / name)}.stl");')
        y -= hi[1] - lo[1] + gap
    return "\n".join(lines) + "\n"


def system_scene(p):
    """Inhaler (schematic) -> chamber -> cat face mask, assembled."""
    cap_z = p["z_top"] - p["skirt_h"]
    mask_z = cap_z + p["z_lid"]          # the mask socket mates with the nozzle over its whole length
    h, w, r = p["mouth_h"], p["mouth_w"], p["mouth_corner_r"]
    # schematic pMDI, modelled upright (boot along +Z, mouthpiece along +X) and turned so the mouthpiece
    # points up into the chamber socket, its tip 3 mm inside
    return f"""
color("{RIGID_COLOR}") import("{scad_path(STL / 'holding_chamber_body.stl')}");
color("{RIGID_COLOR}") translate([0, 0, {cap_z}]) import("{scad_path(STL / 'holding_chamber_cap.stl')}");
color("{TPU_COLOR}") translate([0, 0, {mask_z}]) import("{scad_path(STL / 'cat_face_inhaler_mask.stl')}");
translate([12, 0, 3 - 36]) rotate([0, -90, 0]) {{
    color("{INHALER_COLOR}") {{
        hull() for (x = [-4, 4]) translate([x, 0, 0]) cylinder(d = 26, h = 62, $fn = 48);
        translate([0, 0, 12]) rotate([0, 90, 0]) linear_extrude(36)
            offset(r = {r}) square([{h - 2 * r}, {w - 2 * r}], center = true);
    }}
    color("#d8d8dc") translate([0, 0, 40]) cylinder(d = 22, h = 52, $fn = 64);
}}
"""


def build_diagrams(openscad, workers):
    p = chamber_params(openscad)
    print("  composed scenes (from the STLs in stl/)")
    failures = run_jobs([
        ("print_layout.png", scene_job(openscad, "print_layout", print_layout_scene(), (55, 20), 520)),
        ("system_assembled.png", scene_job(openscad, "system_assembled", system_scene(p), (75, 25), 480)),
    ], workers)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        sys.dont_write_bytecode = True   # keep __pycache__ out of the repo
        import diagrams
    except ImportError as e:
        print(f"  skipping the matplotlib diagrams ({e}); install them with: pip install -r scripts/requirements.txt")
        return failures
    print("  labelled diagrams (matplotlib)")
    for out in diagrams.build(STL, IMG, p, colors={"tpu": TPU_COLOR, "rigid": RIGID_COLOR}):
        print(f"  {out.name}")
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("targets", nargs="*", metavar="target", help="stl, png, svg, diagrams (default: all)")
    ap.add_argument("--openscad", help="path to the OpenSCAD executable")
    ap.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 4, help="parallel OpenSCAD runs")
    args = ap.parse_args()
    all_targets = ["stl", "png", "svg", "diagrams"]
    unknown = set(args.targets) - set(all_targets)
    if unknown:
        ap.error(f"unknown target(s) {', '.join(sorted(unknown))}; choose from {', '.join(all_targets)}")
    targets = set(args.targets or all_targets)
    openscad = find_openscad(args.openscad)
    STL.mkdir(exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    print(f"OpenSCAD: {openscad}")

    t0, failures = time.time(), 0
    jobs = []
    if "stl" in targets:
        jobs += [(f"stl/{n}.stl", (lambda n=n, s=s, p=p: stl_job(openscad, n, s, p))) for n, s, p in STLS]
    if "png" in targets:
        jobs += [(f"docs/img/{n}.png", (lambda n=n, s=s, r=r, p=p: png_job(openscad, IMG / f"{n}.png", SCAD / s, r, p)))
                 for n, s, r, p in PNGS]
    if "svg" in targets:
        jobs.append(("docs/cat_face_rim_template.svg",
                     lambda: run_openscad(openscad, DOCS / "cat_face_rim_template.svg", SCAD / MASK, {"part": "template"})))
    if jobs:
        failures += run_jobs(jobs, args.jobs)
    if "diagrams" in targets:
        failures += build_diagrams(openscad, args.jobs)

    print(f"done in {time.time() - t0:.0f} s" + (f", {failures} FAILED" if failures else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
