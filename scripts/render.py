#!/usr/bin/env python3
"""Regenerate the STLs, renders and diagrams from the OpenSCAD sources.

    python scripts/render.py                 # everything
    python scripts/render.py stl             # only the STLs in stl/
    python scripts/render.py png svg         # only the OpenSCAD renders and the paper template
    python scripts/render.py diagrams        # only the composed scenes and labelled diagrams

Targets:
    stl       printable parts (binary STL): both masks for every cat weight in SIZES -> stl/<weight>kg/,
              the holding chamber parts, which fit every size -> stl/common/
    png       OpenSCAD renders of single parts -> docs/img/*.png
    svg       1:1 paper template of the cat face mask rim for every weight -> stl/<weight>kg/
    diagrams  scenes composed from the exported STLs (print layout, mask sizes, assembled system)
              and the labelled sections drawn with matplotlib -> docs/img/*.png

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

# cat weights (kg) the masks are exported for; each gets stl/<weight>kg/ with both masks and the paper template
SIZES = [3.3, 4, 5, 6]
# the cat_weight_kg default in the mask files: the renders and diagrams in docs/ show this size
DOCS_SIZE = 3.3

# holding chamber parts, the same for every size (slowest first): output name, parameter overrides
COMMON = [
    ("holding_chamber_one_piece_spacer", {"part": "body", "one_piece": True, "valve": False}),
    ("holding_chamber_cap", {"part": "cap"}),
    ("holding_chamber_body", {"part": "body"}),
    ("holding_chamber_valve_insert", {"part": "insert"}),
    ("holding_chamber_valve_flap", {"part": "flap"}),
    ("holding_chamber_umbrella", {"part": "umbrella"}),
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

PNG_OPTS = ["--viewall", "--autocenter", "--projection=p", "--colorscheme=Tomorrow"]

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


def size_name(kg):
    return f"{kg:g}kg"


def mask_stl(name, kg):
    return STL / size_name(kg) / f"{name}_{size_name(kg)}.stl"


def template_svg(kg):
    return STL / size_name(kg) / f"cat_face_rim_template_{size_name(kg)}.svg"


def common_stl(name):
    return STL / "common" / f"{name}.stl"


def stl_targets():
    """(output, source, parameter overrides) for every STL, the slow ones first."""
    def masks(name, src):
        return [(mask_stl(name, kg), src, {"cat_weight_kg": kg}) for kg in SIZES]
    common = [(common_stl(name), CHAMBER, params) for name, params in COMMON]
    return masks("round_cushion_inhaler_mask", ROUND) + common + masks("cat_face_inhaler_mask", MASK)


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def export_job(openscad, out, src, params, extra=()):
    def job():
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        return run_openscad(openscad, out, SCAD / src, params, extra)
    return job


def png_job(openscad, out, src, rot, params, distance=300, size=(1400, 1050), fit=True):
    """fit: centre and zoom to the whole model; otherwise the camera looks at the origin from the given distance."""
    camera = f"--camera=0,0,0,{rot[0]},0,{rot[1]},{distance}"
    opts = PNG_OPTS if fit else [o for o in PNG_OPTS if o not in ("--viewall", "--autocenter")]
    return run_openscad(openscad, out, src, params, opts + [f"--imgsize={size[0]},{size[1]}", camera])


def run_jobs(jobs, workers):
    """jobs: list of (label, callable). Prints one line per job; returns the number of failures."""
    failures = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [(label, pool.submit(fn)) for label, fn in jobs]
        for label, fut in futures:
            try:
                secs, issues = fut.result()
                print(f"  {label:<52} {secs:6.1f} s")
                for line in issues:
                    print(f"      {line}")
            except RuntimeError as e:
                failures += 1
                print(f"  {label:<52} FAILED")
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


def scene_job(openscad, name, scad_text, rot, distance, size=(1400, 1050), fit=True):
    def job():
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / f"{name}.scad"
            src.write_text(scad_text, encoding="utf-8")
            return png_job(openscad, IMG / f"{name}.png", src, rot, {}, distance, size, fit)
    return job


def placed(path, color, x, y, z):
    return f'color("{color}") translate([{x:.2f}, {y:.2f}, {z:.2f}]) import("{scad_path(path)}");'


def print_layout_scene():
    """Every printable part as exported (masks at the docs size), in print orientation, coloured by material."""
    big = [(common_stl("holding_chamber_body"), RIGID_COLOR), (common_stl("holding_chamber_cap"), RIGID_COLOR),
           (mask_stl("cat_face_inhaler_mask", DOCS_SIZE), TPU_COLOR),
           (mask_stl("round_cushion_inhaler_mask", DOCS_SIZE), TPU_COLOR)]
    small = [(common_stl("holding_chamber_valve_insert"), RIGID_COLOR), (common_stl("holding_chamber_valve_flap"), TPU_COLOR),
             (common_stl("holding_chamber_umbrella"), TPU_COLOR)]
    gap = 10
    lines, x = [], 0.0
    for path, color in big:
        lo, hi = stl_bounds(path)
        lines.append(placed(path, color, x - lo[0], -(lo[1] + hi[1]) / 2, -lo[2]))
        x += hi[0] - lo[0] + gap
    # small parts in a column in front of the body
    y = None
    for path, color in small:
        lo, hi = stl_bounds(path)
        if y is None:
            y = -max(20.0, (hi[1] - lo[1]) / 2) - gap
        lines.append(placed(path, color, -lo[0] - (hi[0] - lo[0]) - gap, y - hi[1], -lo[2]))
        y -= hi[1] - lo[1] + gap
    return "\n".join(lines) + "\n"


def mask_sizes_scene():
    """Both masks for every size side by side (cat face behind, round in front), labelled with the cat weight."""
    rows = ["cat_face_inhaler_mask", "round_cushion_inhaler_mask"]
    gap, row_gap = 12, 30
    bounds = {(name, kg): stl_bounds(mask_stl(name, kg)) for name in rows for kg in SIZES}
    depth = {name: max(hi[1] - lo[1] for (n, _), (lo, hi) in bounds.items() if n == name) for name in rows}
    row_y = {rows[0]: 0.0, rows[1]: -(depth[rows[0]] + depth[rows[1]]) / 2 - row_gap}
    label_y = row_y[rows[1]] - depth[rows[1]] / 2 - 22
    height = max(hi[2] - lo[2] for lo, hi in bounds.values())
    lines, x = [], 0.0
    for kg in SIZES:
        width = max(bounds[name, kg][1][0] - bounds[name, kg][0][0] for name in rows)
        cx = x + width / 2
        for name in rows:
            lo, hi = bounds[name, kg]
            lines.append(placed(mask_stl(name, kg), TPU_COLOR, cx - (lo[0] + hi[0]) / 2, row_y[name] - (lo[1] + hi[1]) / 2, -lo[2]))
        lines.append(f'color("#4a4a4a") translate([{cx:.2f}, {label_y:.2f}, 0]) linear_extrude(0.6) '
                     f'text("{kg:g} kg", size = 8, halign = "center", font = "Liberation Sans:style=Bold");')
        x += width + gap
    # centred on the origin, where the fixed camera looks
    cx, cy, cz = (x - gap) / 2, (depth[rows[0]] / 2 + label_y - 4) / 2, height / 2
    return f"translate([{-cx:.2f}, {-cy:.2f}, {-cz:.2f}]) {{\n" + "\n".join(lines) + "\n}\n"


def system_scene(p):
    """Inhaler (schematic) -> chamber -> cat face mask, assembled."""
    cap_z = p["z_top"] - p["skirt_h"]
    mask_z = cap_z + p["z_lid"]          # the mask socket mates with the nozzle over its whole length
    h, w, r = p["mouth_h"], p["mouth_w"], p["mouth_corner_r"]
    # schematic pMDI, modelled upright (boot along +Z, mouthpiece along +X) and turned so the mouthpiece
    # points up into the chamber socket, its tip 3 mm inside
    return f"""
{placed(common_stl("holding_chamber_body"), RIGID_COLOR, 0, 0, 0)}
{placed(common_stl("holding_chamber_cap"), RIGID_COLOR, 0, 0, cap_z)}
{placed(mask_stl("cat_face_inhaler_mask", DOCS_SIZE), TPU_COLOR, 0, 0, mask_z)}
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
        ("mask_sizes.png", scene_job(openscad, "mask_sizes", mask_sizes_scene(), (55, 0), 560, (1600, 900), fit=False)),
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
    stls = {"body": common_stl("holding_chamber_body"), "cap": common_stl("holding_chamber_cap"),
            "insert": common_stl("holding_chamber_valve_insert"), "umbrella": common_stl("holding_chamber_umbrella"),
            "cat_face": mask_stl("cat_face_inhaler_mask", DOCS_SIZE),
            "round": mask_stl("round_cushion_inhaler_mask", DOCS_SIZE)}
    for out in diagrams.build(stls, IMG, p, colors={"tpu": TPU_COLOR, "rigid": RIGID_COLOR}):
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
        jobs += [(rel(out), export_job(openscad, out, src, params, ["--export-format", "binstl"]))
                 for out, src, params in stl_targets()]
    if "png" in targets:
        jobs += [(f"docs/img/{n}.png", (lambda n=n, s=s, r=r, p=p: png_job(openscad, IMG / f"{n}.png", SCAD / s, r, p)))
                 for n, s, r, p in PNGS]
    if "svg" in targets:
        jobs += [(rel(template_svg(kg)), export_job(openscad, template_svg(kg), MASK, {"part": "template", "cat_weight_kg": kg}))
                 for kg in SIZES]
    if jobs:
        failures += run_jobs(jobs, args.jobs)
    if "diagrams" in targets:
        failures += build_diagrams(openscad, args.jobs)

    print(f"done in {time.time() - t0:.0f} s" + (f", {failures} FAILED" if failures else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
