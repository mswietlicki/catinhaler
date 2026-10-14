#!/usr/bin/env python3
"""Build the Polish website (GitHub Pages) into _site/.

    python scripts/build_site.py

Copies the hand-written pages from site/ and the images from docs/img/, copies the printable
files from stl/ under Polish names that start with the material (TPU_, PETG_, PAPIER_), packs one
ZIP per cat size, and fills in the download cards (index.html) and the printable template sheet
(szablony.html). Only the Python standard library is needed, so .github/workflows/pages.yml runs
it on every push to main. It packages what is already in stl/ and docs/img/: run render.py first
when the .scad files change.
"""
import html
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site"
OUT = ROOT / "_site"
STL = ROOT / "stl"
IMG = ROOT / "docs" / "img"
FILES = "pliki"       # download folder on the site

# repo name -> (Polish file name, description, material, how many to print); CHAMBER is listed in this order
MASKS = {
    "cat_face_inhaler_mask": ("TPU_maska_profilowana", "Maska profilowana (dopasowana do pyszczka)", "TPU",
                              "1 szt., wybierz jedną z dwóch masek"),
    "round_cushion_inhaler_mask": ("TPU_maska_okragla", "Maska okrągła z miękkim wałkiem", "TPU",
                                   "1 szt., wybierz jedną z dwóch masek"),
}
TEMPLATE = ("PAPIER_szablon_maski", "Szablon maski profilowanej", "papier", "1 szt.")
CHAMBER = {
    "holding_chamber_body": ("PETG_komora_korpus", "Korpus komory", "PETG", "1 szt."),
    "holding_chamber_cap": ("PETG_komora_pokrywka", "Pokrywka komory", "PETG", "1 szt."),
    "holding_chamber_valve_insert": ("PETG_zawor_wkladka", "Wkładka zaworu wdechowego", "PETG", "1 szt."),
    "holding_chamber_valve_flap": ("TPU_zawor_klapka", "Klapka (zawór wdechowy)", "TPU", "2–3 szt."),
    "holding_chamber_umbrella": ("TPU_zawor_parasolka", "Parasolka (zawór wydechowy)", "TPU", "2–3 szt."),
    "holding_chamber_one_piece_spacer": ("PETG_komora_jednoczesciowa_bez_zaworow", "Komora jednoczęściowa bez zaworów", "PETG",
                                         "tylko zamiast korpusu, pokrywki i zaworów"),
    "holding_chamber_socket_test": ("PETG_test_gniazda_inhalatora", "Próbka gniazda na inhalator (test dopasowania)", "PETG",
                                    "opcjonalnie, przed korpusem"),
}
MATERIAL_CLASS = {"TPU": "tpu", "PETG": "petg", "papier": "paper"}


def repo_slug():
    """owner/name of the GitHub repository (from Actions, else from the git remote)."""
    slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not slug:
        res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=ROOT)
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", res.stdout.strip())
        slug = m.group(1) if m else "mswietlicki/catinhaler"
    return slug


def weight(folder):
    return float(folder.name[:-2])


def pl_weight(kg):
    return f"{kg:g}".replace(".", ",") + " kg"


def mb(path):
    return f"{path.stat().st_size / 1e6:.1f}".replace(".", ",") + " MB"


def copy_files(size_dirs):
    """Copy the printable files under their Polish names; returns {size name: [(path, info)]} and the chamber list."""
    sizes = {}
    for d in size_dirs:
        entries = []
        for repo_name, info in MASKS.items():
            dst = OUT / FILES / d.name / f"{info[0]}_{d.name}.stl"
            shutil.copyfile(d / f"{repo_name}_{d.name}.stl", dst)
            entries.append((dst, info))
        dst = OUT / FILES / d.name / f"{TEMPLATE[0]}_{d.name}.svg"
        shutil.copyfile(IMG / "pl" / f"cat_face_rim_template_{d.name}.svg", dst)
        entries.append((dst, TEMPLATE))
        sizes[d.name] = entries
    present = {p.stem: p for p in (STL / "common").glob("*.stl")}
    unknown = sorted(set(present) - set(CHAMBER))
    if unknown:
        sys.exit(f"stl/common/{unknown[0]}.stl has no Polish name: add it to CHAMBER in {Path(__file__).name}")
    chamber = []
    for repo_name, info in CHAMBER.items():
        if repo_name in present:
            dst = OUT / FILES / "komora" / f"{info[0]}.stl"
            shutil.copyfile(present[repo_name], dst)
            chamber.append((dst, info))
    return sizes, chamber


def readme(size, entries, chamber, site):
    """CZYTAJ_MNIE.txt inside each ZIP (Windows friendly: UTF-8 with BOM, CRLF)."""
    kg = pl_weight(float(size[:-2]))
    width = max(len(p.name) for p, _ in entries + chamber) + 2
    by_mat = {}
    for p, info in entries + chamber:
        by_mat.setdefault(info[2], []).append((p.name, f"{info[1]}: {info[3]}"))
    lines = [
        f"CatInhaler: maska i komora inhalacyjna dla kota ok. {kg}",
        "",
        f"Instrukcja krok po kroku: {site}",
        "",
        "UWAGA: to projekt hobbystyczny, nie wyrób medyczny. Lek i dawkowanie ustala lekarz weterynarii.",
        "",
        "CO WYDRUKOWAĆ",
        "",
        "Najpierw na papierze (sprawdź rozmiar maski):",
        *[f"  {n:<{width}}{d}" for n, d in by_mat["papier"]],
        f"  Szablon najlepiej wydrukować ze strony {site}szablony.html w skali 100 %.",
        "",
        "Z elastycznego filamentu TPU 95A:",
        *[f"  {n:<{width}}{d}" for n, d in by_mat["TPU"]],
        "",
        "Ze sztywnego PETG (może być PLA):",
        *[f"  {n:<{width}}{d}" for n, d in by_mat["PETG"]],
        "",
        "USTAWIENIA DRUKU",
        "",
        "  Dysza 0,4 mm, warstwa 0,2 mm, bez podpór, każda część w ułożeniu z pliku.",
        "  TPU: 220-235 °C, stół 40-50 °C, 20-30 mm/s. Maska 4-5 obrysów, klapka i parasolka 100 % wypełnienia.",
        "       Wysusz filament przed drukiem.",
        "  PETG: 235-250 °C, stół 75-85 °C, 5 obrysów, brim 5 mm pod korpusem.",
        "",
        "Po wydruku usuń nitki i ostre krawędzie: maska dotyka pyszczka kota.",
        "",
    ]
    return "\r\n".join(lines)


def make_zip(size, entries, chamber, site):
    path = OUT / FILES / f"catinhaler-{size}.zip"
    top = f"catinhaler-{size}"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(f"{top}/CZYTAJ_MNIE.txt", readme(size, entries, chamber, site).encode("utf-8-sig"))
        for p, _ in entries + chamber:
            z.write(p, f"{top}/{p.name}")
    return path


def file_item(path, info):
    rel = path.relative_to(OUT).as_posix()
    mat = info[2]
    return (f'<li><span class="mat {MATERIAL_CLASS[mat]}">{html.escape(mat)}</span>'
            f'<a href="{rel}" download>{html.escape(path.name)}</a>: {html.escape(info[1])}</li>')


def downloads_html(sizes, zips, chamber):
    cards = []
    for size, entries in sizes.items():
        z = zips[size]
        cards.append(
            '<article class="download">\n'
            f'  <h3>Kot ok. {pl_weight(float(size[:-2]))}</h3>\n'
            '  <p class="sub">obie maski, szablon i cała komora</p>\n'
            f'  <a class="button" href="{z.relative_to(OUT).as_posix()}" download>Pobierz komplet '
            f'<span class="meta">ZIP, {mb(z)}</span></a>\n'
            '  <details><summary>Pojedyncze pliki</summary><ul>\n    '
            + "\n    ".join(file_item(p, info) for p, info in entries)
            + '\n  </ul></details>\n</article>')
    chamber_list = "\n  ".join(file_item(p, info) for p, info in chamber)
    return (f'<div class="downloads">\n{chr(10).join(cards)}\n</div>\n'
            '<details class="more"><summary>Pojedyncze pliki komory (wspólne dla wszystkich rozmiarów)</summary>\n'
            f'<ul class="files">\n  {chamber_list}\n</ul>\n</details>')


def svg_size_mm(path):
    m = re.search(r'<svg[^>]*\swidth="([\d.]+)mm"[^>]*\sheight="([\d.]+)mm"', path.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"{path}: no width/height in mm")
    return float(m.group(1)), float(m.group(2))


def templates_html(sizes):
    figs = []
    for size, entries in sizes.items():
        svg = next(p for p, info in entries if info is TEMPLATE)
        w, h = svg_size_mm(svg)
        figs.append(f'<figure class="template"><img src="{svg.relative_to(OUT).as_posix()}" '
                    f'style="width: {w:g}mm; height: {h:g}mm" alt="Szablon maski dla kota ok. {pl_weight(float(size[:-2]))}">'
                    f'<figcaption>kot ok. {pl_weight(float(size[:-2]))}</figcaption></figure>')
    return "\n      ".join(figs)


SKIP_BLOCKS = re.compile(r"(<(script|style|pre|textarea)\b.*?</\2>)", re.S | re.I)


def no_orphans(page):
    """Polish typesetting: keep one-letter words (a, i, o, u, w, z) with the next word (non-breaking space)."""
    def text(chunk):
        return re.sub(r">([^<]+)<", lambda m: ">" + re.sub(r"(?<![\w&;])([aiouwzAIOUWZ]) ", "\\1&nbsp;", m.group(1)) + "<", chunk)
    parts = SKIP_BLOCKS.split(page)
    # split() with two groups yields: text, whole block, tag name, text, ...
    out = []
    for i in range(0, len(parts), 3):
        out.append(text(parts[i]))
        if i + 1 < len(parts):
            out.append(parts[i + 1])
    return "".join(out)


def check_links(pages):
    """Every local href/src must point at a file in _site/."""
    bad = []
    for page in pages:
        for ref in re.findall(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"', page.read_text(encoding="utf-8")):
            if re.match(r"^(https?:|mailto:|data:)", ref):
                continue
            if not (page.parent / ref).is_file():
                bad.append(f"{page.name}: {ref}")
    if bad:
        sys.exit("broken links:\n  " + "\n  ".join(bad))


def main():
    slug = repo_slug()
    owner, name = slug.split("/", 1)
    repo_url, site_url = f"https://github.com/{slug}", f"https://{owner.lower()}.github.io/{name}/"

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    shutil.copytree(IMG, OUT / "img")
    size_dirs = sorted((d for d in STL.glob("*kg") if d.is_dir()), key=weight)
    for d in size_dirs:
        (OUT / FILES / d.name).mkdir(parents=True)
    (OUT / FILES / "komora").mkdir(parents=True)

    sizes, chamber = copy_files(size_dirs)
    zips = {size: make_zip(size, entries, chamber, site_url) for size, entries in sizes.items()}

    fill = {"<!-- @pobierz -->": downloads_html(sizes, zips, chamber), "<!-- @szablony -->": templates_html(sizes)}
    pages = sorted(OUT.glob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for marker, content in fill.items():
            text = text.replace(marker, content)
        text = no_orphans(text.replace("@@REPO@@", repo_url).replace("@@SITE@@", site_url))
        page.write_text(text, encoding="utf-8")
    check_links(pages)

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"site: {OUT.relative_to(ROOT)}/  ({len(pages)} pages, {len(zips)} ZIPs, {total / 1e6:.1f} MB)  ->  {site_url}")


if __name__ == "__main__":
    main()
