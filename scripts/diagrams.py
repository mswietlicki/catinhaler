"""Labelled 2D diagrams for the manual, drawn from the exported STLs.

Called by render.py (target "diagrams"), which passes the holding chamber dimensions
evaluated by OpenSCAD, so the drawings follow the .scad parameters.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.colors import to_rgb
from matplotlib.patches import Circle, Ellipse, PathPatch, Polygon, Rectangle
from matplotlib.path import Path as MplPath
from shapely.geometry.polygon import orient

FONT = 9.5
TEXT_H = 0.16      # height of one text line in inches at FONT size, for spacing labels

# translations of the diagram labels, keyed by the English text (format fields are filled in after translating)
TEXT = {"pl": {
    # chamber section
    "Holding chamber, cut through the assembled parts": "Komora inhalacyjna w przekroju, po złożeniu",
    "aerosol flow": "przepływ leku",
    "wedge socket: the inhaler mouthpiece pushes in\n(tapers {taper} mm over {depth} mm)":
        "gniazdo: tu wciskasz ustnik inhalatora\n(zwęża się o {taper} mm na długości {depth} mm)",
    "inlet cone": "stożek wlotowy",
    "chamber body: {d} mm OD, {wall} mm wall": "korpus komory: średnica {d} mm, ścianka {wall} mm",
    "cap skirt: push fit inside the body": "kołnierz pokrywki: wciskany w korpus",
    "inhalation valve insert:\npress fit in the cap bore": "wkładka zaworu wdechowego:\nwciśnięta w pokrywkę",
    "flap (TPU {t} mm): lifts on inhalation,\nseals on the grille on exhalation":
        "klapka (TPU {t} mm): unosi się przy wdechu,\nprzy wydechu przylega do kratki",
    "exhalation umbrella (TPU {t} mm) in the lid\npocket: exhaled air leaves the chamber here":
        "parasolka (TPU {t} mm) w kieszonce pokrywki:\ntędy wydychane powietrze wychodzi na zewnątrz",
    "nozzle: same shape as the inhaler\nmouthpiece, plugs into the mask":
        "króciec: ma kształt ustnika inhalatora,\nwkłada się go w maskę",
    "ceiling cone:\nroom for the flap to open": "stożek pod pokrywką:\nmiejsce na otwarcie klapki",
    "cap": "pokrywka",
    "body": "korpus",
    # valve assembly
    "1. valve insert from the nozzle side": "1. wkładka zaworu od strony króćca",
    "hinge slot": "szczelina",
    "grille: the closed flap rests on it": "kratka: opiera się na niej zamknięta klapka",
    "2. flap, printed flat in TPU ({t} mm)": "2. klapka, drukowana płasko z TPU ({t} mm)",
    "covers the opening (dashed)\nwith {o} mm overlap": "zakrywa otwór\n(linia przerywana)\nz zakładką {o} mm",
    "tab goes through the slot": "języczek przechodzi przez szczelinę",
    "bulb: squeezes through,\nthen locks underneath": "kulka: przeciśnij\nprzez szczelinę, zablokuje\nsię pod spodem",
    "3. assembled valve, side view (thickness exaggerated)": "3. złożony zawór z boku (grubość powiększona)",
    "flap lies flat on the insert": "klapka leży płasko\nna wkładce",
    "opens this way\non inhalation": "otwiera się\nprzy wdechu",
    "tab bent 90 deg through the slot;\nthe bulb holds it from below": "języczek zgięty w szczelinie,\nkulka trzyma go od spodu",
    "chamber side (grille face)": "strona komory (kratka)",
    "nozzle / mask side": "strona króćca i maski",
    # mask orientation
    "Cat face mask orientation (side view, cut in half)": "Jak założyć maskę profilowaną (widok z boku, przekrój)",
    "shallow, wide side of the rim:\nover the bridge of the nose, below the eyes":
        "płytsza, szersza strona brzegu:\nna grzbiecie nosa, poniżej oczu",
    "deep, narrow side of the rim:\nunder the chin": "głębsza, węższa strona brzegu:\npod brodą",
    "socket: inhaler or\nchamber nozzle": "gniazdo: inhalator\nalbo króciec komory",
    "Schematic. The rim must cover nose and mouth and stay below the eyes.":
        "Schemat. Brzeg maski musi zakrywać nos i pyszczek i zostać poniżej oczu.",
}}


DECIMAL = {"pl": ","}


def T(lang, text, **fields):
    """The label in the given language (English when there is no translation), with its fields filled in."""
    sep = DECIMAL.get(lang, ".")
    return TEXT.get(lang, {}).get(text, text).format(**{k: str(v).replace(".", sep) for k, v in fields.items()})


def shade(color, f):
    """f < 1 darkens, f > 1 lightens towards white."""
    c = np.array(to_rgb(color))
    return tuple(c * f) if f <= 1 else tuple(c + (1 - c) * (f - 1))


def load(path):
    m = trimesh.load(path, force="mesh")
    if m.volume < 0:
        m.invert()
    return m


def moved(mesh, dx=0.0, dz=0.0, flip=False):
    m = mesh.copy()
    if flip:  # upside down (rotate 180 deg about X)
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation([dx, 0, dz])
    return m


def xz_section(mesh):
    """Polygons (exterior, [holes]) of the cut through the plane y = 0, in (x, z)."""
    s = mesh.section(plane_origin=[0, 0, 0], plane_normal=[0, 1, 0])
    if s is None:
        return []
    planar, to_3d = s.to_2D()

    def xz(coords):
        c = np.asarray(coords)
        return trimesh.transform_points(np.column_stack([c, np.zeros(len(c))]), to_3d)[:, [0, 2]]

    out = []
    for poly in planar.polygons_full:
        poly = orient(poly)  # exterior and holes wound in opposite directions so holes stay empty
        out.append((xz(poly.exterior.coords), [xz(h.coords) for h in poly.interiors]))
    return out


def fill(ax, polys, color, transform=None, **kw):
    for ext, holes in polys:
        rings = [ext] + holes
        if transform is not None:
            rings = [transform(r) for r in rings]
        codes = []
        for r in rings:
            codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(r) - 2) + [MplPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MplPath(np.concatenate(rings), codes), facecolor=color, edgecolor="none", **kw))


def spread(ys, gaps):
    """Move label heights apart (keeping their order) so neighbours are at least gaps[i] apart."""
    order = np.argsort(ys)
    out = np.array(ys, float)
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        need = (gaps[i] + gaps[j]) / 2
        if out[j] - out[i] < need:
            out[j] = out[i] + need
    return out


def label_column(ax, labels, x_text, ha):
    """labels: (text, anchor_xy, wanted_y). Places the texts in a column at x_text without overlaps.
    Call after the axis limits and aspect are set."""
    ax.apply_aspect()
    y0, y1 = ax.get_ylim()
    line = TEXT_H * (y1 - y0) / (ax.get_position().height * ax.figure.get_figheight())
    gaps = [(t.count("\n") + 2) * line for t, _, _ in labels]
    ys = spread([y for _, _, y in labels], gaps)
    for (txt, xy, _), y in zip(labels, ys):
        ax.annotate(txt, xy=xy, xytext=(x_text, y), fontsize=FONT, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="->", lw=0.8, shrinkA=3, shrinkB=0))


def save(fig, path):
    fig.savefig(path, dpi=110, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return Path(path)


# ---------------------------------------------------------------- holding chamber section
def chamber_section(m, p, c, out, lang="en"):
    cap_z = p["z_top"] - p["skirt_h"]
    insert_z = cap_z + p["z_c"] - p["insert_t"]
    flap_z = cap_z + p["z_c"]
    umb = moved(m["umbrella"], p["r_ex"], cap_z + p["seat_z"] + p["umbrella_t"], flip=True)
    top = cap_z + p["cap_h"]
    half = p["lid_d"] / 2

    xlim, ylim = (-half - 52, half + 58), (-6, top + 6)
    fig_h = 11.5
    fig_w = fig_h * (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor="white")
    fill(ax, xz_section(m["body"]), c["body"])
    fill(ax, xz_section(moved(m["cap"], dz=cap_z)), c["cap"])
    fill(ax, xz_section(moved(m["insert"], dz=insert_z)), c["insert"])
    fill(ax, xz_section(umb), c["tpu"])
    # flap lying closed on the insert, its tab bent down through the hinge slot, bulb underneath
    fd, ft = p["flap_d"], p["flap_t"]
    ax.add_patch(Rectangle((-fd / 2, flap_z), fd, ft, color=c["tpu"]))
    neck = p["insert_t"] + 1.2
    ax.add_patch(Rectangle((p["hinge_r"] - ft / 2, flap_z - neck), ft, neck, color=c["tpu"]))
    ax.add_patch(Ellipse((p["hinge_r"], flap_z - neck), 2.2, 1.2, color=c["tpu"]))

    ax.annotate("", xy=(0, cap_z - 4), xytext=(0, p["z_cone"] + 8), arrowprops=dict(arrowstyle="-|>", lw=2.2, color="0.35"))
    ax.text(1.5, (cap_z + p["z_cone"]) / 2, T(lang, "aerosol flow"), fontsize=FONT, color="0.35", rotation=90, va="center")

    wall, sh = p["wall"], p["socket_taper"] / 2
    z_mid_cone = (p["z_sock"] + p["z_cone"]) / 2
    x_mid_cone = (p["ma"] - sh + p["Ri"]) / 2 + wall / 2
    right = [
        (T(lang, "wedge socket: the inhaler mouthpiece pushes in\n(tapers {taper} mm over {depth} mm)",
           taper=f"{p['socket_taper']:g}", depth=f"{p['socket_taper_depth']:g}"),
         (p["ma"] + wall / 2, p["socket_taper_depth"] / 3), p["socket_taper_depth"] / 3),
        (T(lang, "inlet cone"), (x_mid_cone, z_mid_cone), z_mid_cone),
        (T(lang, "chamber body: {d} mm OD, {wall} mm wall", d=f"{p['chamber_d']:g}", wall=f"{wall:g}"),
         (p["chamber_d"] / 2 - wall / 2, p["z_cone"] + p["chamber_len"] / 2), p["z_cone"] + p["chamber_len"] / 2),
        (T(lang, "cap skirt: push fit inside the body"), ((p["skirt_od"] + p["bore_d"]) / 4, cap_z + p["skirt_h"] / 2), cap_z),
        (T(lang, "inhalation valve insert:\npress fit in the cap bore"), (p["bore_d"] / 2 - 2.5, insert_z + p["insert_t"] / 2),
         insert_z - 2),
        (T(lang, "flap (TPU {t} mm): lifts on inhalation,\nseals on the grille on exhalation", t=f"{ft:g}"),
         (p["hinge_r"] - 5, flap_z + ft / 2), flap_z + 2),
        (T(lang, "exhalation umbrella (TPU {t} mm) in the lid\npocket: exhaled air leaves the chamber here", t=f"{p['umbrella_t']:g}"),
         (p["r_ex"] + p["umbrella_d"] / 2 - 1, cap_z + p["seat_z"] + p["umbrella_t"] / 2), cap_z + p["seat_z"] + 4),
        (T(lang, "nozzle: same shape as the inhaler\nmouthpiece, plugs into the mask"),
         (p["na"] - p["nt"] / 2 - 0.8, cap_z + p["z_lid"] + p["nozzle_len"] / 2), cap_z + p["z_lid"] + p["nozzle_len"] / 2 + 4),
    ]
    z_ceiling = cap_z + (p["z_c"] + p["z_n"]) / 2
    x_ceiling = -((p["bore_d"] / 2 + p["na"] - 1.6) / 2 + 1.2)
    left = [(T(lang, "ceiling cone:\nroom for the flap to open"), (x_ceiling, z_ceiling), z_ceiling),
            (T(lang, "cap"), (-half + 1, cap_z + p["z_lid"] - 1), cap_z + p["z_lid"] + 6),
            (T(lang, "body"), (-p["chamber_d"] / 2 + 0.5, p["z_cone"] + 20), p["z_cone"] + 20)]

    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(T(lang, "Holding chamber, cut through the assembled parts"), fontsize=12)
    label_column(ax, right, half + 8, "left")
    label_column(ax, left, -half - 8, "right")
    return save(fig, out)


# ---------------------------------------------------------------- exhalation valve close-up
def exhale_detail(m, p, c, out):
    umb = moved(m["umbrella"], p["r_ex"], p["seat_z"] + p["umbrella_t"], flip=True)
    half = p["lid_d"] / 2
    xlim, ylim = (-4, half + 34), (p["z_c"] - 6, p["cap_h"] + 2)
    fig_h = 7.5
    fig_w = fig_h * (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor="white")
    fill(ax, xz_section(m["cap"]), c["cap"])
    fill(ax, xz_section(umb), c["tpu"])

    # the two angled holes that lie in the cut plane run from the pocket floor down and inwards
    hole_r = p["umbrella_d"] / 2 - p["exhale_hole_d"] / 2 - 1.2
    hole_top = np.array([p["r_ex"] - hole_r, p["seat_z"] + 1])
    hole_xy = hole_top + 4.5 * np.array([-0.7071, -0.7071])
    z_noz = p["z_lid"] + 0.55 * p["nozzle_len"]
    x_noz = p["na"] - p["nt"] * 0.55 - 0.8
    labels = [
        ("nozzle: plugs into the mask", (x_noz, z_noz), z_noz + 3),
        ("pocket, open to the room:\nexhaled air escapes here", (p["r_ex"] + p["pocket_d"] / 2 - 1.5, p["z_lid"] - 1), p["z_lid"] + 1),
        (f"umbrella disc, TPU {p['umbrella_t']:g} mm: lifts on exhalation,\nis sucked flat onto the holes on inhalation",
         (p["r_ex"] + p["umbrella_d"] / 2 - 1.2, p["seat_z"] + p["umbrella_t"] / 2), p["seat_z"] - 1),
        (f"{p['exhale_holes']:g} angled holes, {p['exhale_hole_d']:g} mm:\nvestibule -> pocket", tuple(hole_xy), p["seat_z"] - 5),
        ("stem through the seat; the bulb\nsnaps into the blind pocket below",
         (p["r_ex"] + 0.6, p["seat_z"] - p["seat_t"] - p["bulb_pocket_h"] / 2), p["seat_z"] - 9),
        ("vestibule: mask side of the inhalation flap", (4, p["z_c"] + 2.5), p["z_c"] - 3),
    ]
    ax.axvline(0, color="0.6", lw=0.8, ls="-.")
    ax.text(0.4, ylim[0] + 0.6, "cap axis", fontsize=8, color="0.45")
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title("Exhalation umbrella valve, cut through the cap (right half, print orientation)", fontsize=12)
    label_column(ax, labels, half + 3, "left")
    return save(fig, out)


# ---------------------------------------------------------------- inhalation valve parts and assembly
def valve_assembly(p, c, out, lang="en"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), facecolor="white")
    d = p["bore_d"] - p["insert_clearance"]
    vd, gw, hr = p["valve_d"], p["grille_w"], p["hinge_r"]
    sw, st = p["slot_w"], p["slot_t"]
    tw, ft, it, fd = p["tab_w"], p["flap_t"], p["insert_t"], p["flap_d"]
    neck = it + 1.2
    bulb = tw + 1.6

    ax = axes[0]
    ax.add_patch(Circle((0, 0), d / 2, color=c["insert"]))
    ax.add_patch(Circle((0, 0), vd / 2, color="white"))
    ax.add_patch(Rectangle((-(vd + 1) / 2, -gw / 2), vd + 1, gw, color=c["insert"]))
    ax.add_patch(Rectangle((-gw / 2, -(vd + 1) / 2), gw, vd + 1, color=c["insert"]))
    ax.add_patch(Rectangle((hr - st / 2, -sw / 2), st, sw, color="white", ec="k", lw=0.8))
    ax.annotate(T(lang, "hinge slot"), xy=(hr, sw / 2), xytext=(hr - 3, d / 2 + 2.5), fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.annotate(T(lang, "grille: the closed flap rests on it"), xy=(0, -vd / 2 + 1.5), xytext=(-d / 2, -d / 2 - 3.5), fontsize=FONT + 0.5,
                arrowprops=dict(arrowstyle="->"))
    ax.set_title(T(lang, "1. valve insert from the nozzle side"))
    ax.set_xlim(-d / 2 - 4, d / 2 + 6)
    ax.set_ylim(-d / 2 - 6, d / 2 + 6)

    ax = axes[1]
    ax.add_patch(Circle((0, 0), fd / 2, color=c["tpu"]))
    ax.add_patch(Rectangle((fd / 2 - 0.5, -tw / 2), neck + 0.5, tw, color=c["tpu"]))
    ax.add_patch(Circle((fd / 2 + neck + bulb / 2 - 0.3, 0), bulb / 2, color=c["tpu"]))
    ax.add_patch(Circle((0, 0), vd / 2, fill=False, ec="k", ls="--", lw=0.8))
    ax.annotate(T(lang, "covers the opening (dashed)\nwith {o} mm overlap", o=f"{p['flap_overlap']:g}"), xy=(-vd / 2 * 0.7, -vd / 2 * 0.7),
                xytext=(-fd / 2 - 2, -fd / 2 - 5), fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.annotate(T(lang, "tab goes through the slot"), xy=(fd / 2 + neck / 2, tw / 2), xytext=(fd / 2 - 6, fd / 2 + 3), fontsize=FONT + 0.5,
                arrowprops=dict(arrowstyle="->"))
    ax.annotate(T(lang, "bulb: squeezes through,\nthen locks underneath"), xy=(fd / 2 + neck + bulb / 2, -bulb / 2),
                xytext=(fd / 2 + 1, -fd / 2 - 5), fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.set_title(T(lang, "2. flap, printed flat in TPU ({t} mm)", t=f"{ft:g}"))
    ax.set_xlim(-fd / 2 - 4, fd / 2 + neck + bulb + 6)
    ax.set_ylim(-fd / 2 - 8, fd / 2 + 6)

    ax = axes[2]
    s = 1.6   # thickness exaggeration, so the thin parts are visible
    for x0, w in [(-d / 2, d / 2 - vd / 2), (vd / 2, d / 2 - vd / 2), (-gw / 2, gw)]:
        ax.add_patch(Rectangle((x0, 0), w, it * s, color=c["insert"]))
    ax.add_patch(Rectangle((hr - st / 2, 0), st, it * s, color="white"))
    ax.add_patch(Rectangle((-fd / 2, it * s), fd, ft * s, color=c["tpu"]))
    ax.add_patch(Rectangle((hr - ft * s / 2, -neck * s + it * s), ft * s, neck * s, color=c["tpu"]))
    ax.add_patch(Ellipse((hr, -neck * s + it * s), bulb * 0.45, ft * s * 2.4, color=c["tpu"]))
    ax.annotate(T(lang, "flap lies flat on the insert"), xy=(fd / 4, it * s + ft * s), xytext=(1.5, 7.5), fontsize=FONT + 0.5,
                arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(-fd / 2 + 1, it * s + 5), xytext=(-fd / 2 + 1, it * s + 1.2),
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color=shade(c["tpu"], 0.75)))
    ax.text(-fd / 2 + 2, it * s + 3.6, T(lang, "opens this way\non inhalation"), fontsize=FONT, color=shade(c["tpu"], 0.75), va="center")
    ax.annotate(T(lang, "tab bent 90 deg through the slot;\nthe bulb holds it from below"), xy=(hr + 0.4, -neck * s + it * s),
                xytext=(hr - 15, -7.5), fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.text(0, -10.5, T(lang, "chamber side (grille face)"), ha="center", fontsize=FONT + 0.5)
    ax.text(0, 11.5, T(lang, "nozzle / mask side"), ha="center", fontsize=FONT + 0.5)
    ax.set_title(T(lang, "3. assembled valve, side view (thickness exaggerated)"))
    ax.set_xlim(-d / 2 - 2, d / 2 + 2)
    ax.set_ylim(-12, 13)

    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    return save(fig, out)


# ---------------------------------------------------------------- how the cat face mask sits on the cat
def mask_orientation(m, c, out, lang="en"):
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor="white")
    fur, muzzle = (0.86, 0.83, 0.79), (0.80, 0.76, 0.72)

    # the mask cut through its tilt plane: model +Z (rim) faces the cat, model +X (shallow side) points up,
    # tipped 8 deg so the socket points forward and slightly down
    polys = xz_section(m["cat_face"])
    a = np.radians(-8)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])

    def place(r):
        return np.column_stack([-r[:, 1], r[:, 0]]) @ rot.T

    allp = np.concatenate([place(e) for e, _ in polys])
    top, bottom = allp[np.argmax(allp[:, 1])], allp[np.argmin(allp[:, 1])]
    socket = allp[allp[:, 0] > allp[:, 0].max() - 3].mean(axis=0)

    # schematic cat head drawn against the mask: the rim line is the face, n points from the face into the cup
    span = np.linalg.norm(bottom - top)
    d = (bottom - top) / span
    n = np.array([-d[1], d[0]])
    if np.dot(socket - top, n) < 0:
        n = -n

    def face(t, s):
        return top + t * span * d + s * n

    head_c = face(0.5, -36) + [-4, 6]
    ax.add_patch(Ellipse(head_c, 86, 72, color=fur))
    ax.add_patch(Polygon([head_c + [-26, 24], head_c + [-12, 52], head_c + [0, 30]], closed=True, color=muzzle))
    ax.add_patch(Polygon([face(0.08, -14), face(0.16, 3), face(0.36, 10), face(0.52, 9), face(0.68, 4), face(0.76, -14)],
                         closed=True, color=muzzle))
    ax.add_patch(Ellipse(top + [-9, 6], 5, 6, color="0.15"))
    ax.add_patch(Ellipse(face(0.36, 9), 5, 3.5, color=(0.80, 0.52, 0.52)))
    ax.plot(*np.array([face(0.5, 8), face(0.6, 1)]).T, color="0.25", lw=1)
    fill(ax, polys, c["tpu"], transform=place)

    ax.annotate(T(lang, "shallow, wide side of the rim:\nover the bridge of the nose, below the eyes"), xy=top + [1, 1],
                xytext=(top[0] + 18, top[1] + 16), fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.annotate(T(lang, "deep, narrow side of the rim:\nunder the chin"), xy=bottom + [1, -1], xytext=(bottom[0] + 26, bottom[1] - 8),
                fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.annotate(T(lang, "socket: inhaler or\nchamber nozzle"), xy=socket + [2, 0], xytext=(socket[0] + 12, socket[1] + 14),
                fontsize=FONT + 0.5, arrowprops=dict(arrowstyle="->"))
    ax.text(socket[0] - 20, bottom[1] - 18, T(lang, "Schematic. The rim must cover nose and mouth and stay below the eyes."),
            ha="center", fontsize=FONT + 0.5)
    ax.set_aspect("equal")
    ax.set_xlim(head_c[0] - 46, socket[0] + 50)
    ax.set_ylim(bottom[1] - 22, head_c[1] + 56)
    ax.axis("off")
    ax.set_title(T(lang, "Cat face mask orientation (side view, cut in half)"), fontsize=12)
    return save(fig, out)


# ---------------------------------------------------------------- both masks cut in half
def mask_sections(m, c, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), facecolor="white")
    for ax, mesh, title in [(axes[0], m["cat_face"], "cat face mask, cut along the tilt (deep side left)"),
                            (axes[1], m["round"], "round cushion mask: the hollow rolled lip")]:
        fill(ax, xz_section(mesh), c["tpu"])
        lo, hi = mesh.bounds
        ax.set_xlim(lo[0] - 3, hi[0] + 3)
        ax.set_ylim(lo[2] - 3, hi[2] + 3)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_title(title)
        ax.set_xlabel("mm")
        ax.set_ylabel("mm")
    fig.tight_layout()
    return save(fig, out)


def build(stls, img_dir, p, colors):
    """stls: STL paths keyed body, cap, insert, umbrella, cat_face, round."""
    img_dir = Path(img_dir)
    c = {"tpu": colors["tpu"], "body": shade(colors["rigid"], 1.25), "cap": colors["rigid"],
         "insert": (0.62, 0.62, 0.66)}
    m = {key: load(path) for key, path in stls.items()}
    outs = [
        chamber_section(m, p, c, img_dir / "chamber_section_labeled.png"),
        exhale_detail(m, p, c, img_dir / "exhale_valve_detail.png"),
        valve_assembly(p, c, img_dir / "valve_assembly.png"),
        mask_orientation(m, c, img_dir / "mask_orientation.png"),
        mask_sections(m, c, img_dir / "mask_sections.png"),
    ]
    # translated copies of the diagrams the Polish site uses -> img_dir/<lang>/
    for lang in TEXT:
        (img_dir / lang).mkdir(exist_ok=True)
        outs += [
            chamber_section(m, p, c, img_dir / lang / "chamber_section_labeled.png", lang),
            valve_assembly(p, c, img_dir / lang / "valve_assembly.png", lang),
            mask_orientation(m, c, img_dir / lang / "mask_orientation.png", lang),
        ]
    return outs
