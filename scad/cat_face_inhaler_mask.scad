// =====================================================================
//  Cat Face Inhaler Mask  -  parametric OpenSCAD version
// =====================================================================
//  A parametric remake of the static design "ventolin cat face v4.3mf"
//  ("maschera gatto ventolin v4"): a mask cup that pushes directly onto
//  the mouthpiece of a pMDI inhaler (Ventolin / salbutamol type).
//
//  Geometry of the original was measured from the mesh and is reproduced
//  (rim outline, 16 deg tilted rim, wedge socket, bowl flare).  Everything
//  is driven by parameters so the cup can be scaled to the cat while the
//  inhaler socket stays the same.
//
//  HOW TO USE
//    1. Set cat_weight_kg (3.3 kg -> face scale 0.90 of the original).
//       Or set rim_length / rim_width directly in mm after checking the
//       paper template:  part = "template"  ->  F6 -> export SVG/DXF ->
//       print 1:1 -> hold against the cat's muzzle (it must cover nose
//       and mouth but stay below the eyes).
//    2. Measure your inhaler mouthpiece with calipers and set mouth_w,
//       mouth_h (outer size of the mouthpiece tip).  The socket tapers so
//       the mouthpiece wedges in; TPU stretches, start with clearance 0.
//    3. part = "mask", F6 render, export STL.
//
//  ORIENTATION ON THE CAT
//    The rim is tilted: the -X side is ~13 mm deeper than the +X side and
//    the outline is narrower there.  The deep narrow end most likely goes
//    under the chin, the wide shallow side over the bridge of the nose.
//
//  PRINTING (TPU, 0.4 mm nozzle)
//    - Print socket down, rim up.  No supports needed (max overhang ~50 deg).
//    - Wall thicknesses default to multiples of 0.4 mm:
//        cup_wall 1.6 = 4 perimeters, socket_wall 2.0 = 5 perimeters.
//      Set the slicer to >= 5 perimeters so everything is solid walls.
//    - stem_shape "rounded" keeps the socket wall uniform; the original's
//      elliptical stem thins to ~1 mm at the socket corners.
//    - 0.2 mm layers, slow (20-30 mm/s), retraction low, fan 50-100 %.
//    - TPU shrinks holes slightly: if the inhaler will not go in, raise
//      socket_clearance by 0.3; if it is loose, lower it or raise
//      socket_taper.
//
//  The polyhedron is built as one closed "ring loop" (outer wall up, bead
//  over the rim, inner wall down, socket, bottom) so it renders instantly
//  and is always manifold.  Requires OpenSCAD 2019.05 or newer
//  (2021.01+ / 2025 recommended).
// =====================================================================

/* [Cat size] */
// Your cat's weight. Linear size scales with (weight / reference_weight)^(1/3).
cat_weight_kg = 3.3;
// Weight of the cat the original design is assumed to fit.
reference_weight_kg = 4.5;
// Force the face scale (0 = compute from weight). 1 = exact size of the original.
face_scale_override = 0;
// Rim outline length in mm (along X = tilt direction, outer edge). 0 = from scale. Original 47.4
rim_length = 0;
// Rim outline width in mm (side to side, Y, outer edge). 0 = from scale. Original 50.4
rim_width = 0;

/* [Inhaler socket] */
// Mouthpiece long outer dimension (mm) -> socket opening along Y
mouth_w = 25.4;
// Mouthpiece short outer dimension (mm) -> socket opening along X
mouth_h = 19.6;
// Corner radius of the mouthpiece outline (min(w,h)/2 gives a stadium). Original ~7
mouth_corner_r = 7;
// Total shrink of the socket opening over socket_taper_depth (wedge fit). 0 = straight socket.
socket_taper = 4;
// Depth over which the taper acts (mm)
socket_taper_depth = 15;
// Extra clearance added to the socket opening (TPU 0, PLA 0.3)
socket_clearance = 0;
// Stem height: bottom of socket to start of the cup (mm)
stem_h = 18.7;
// Stem wall thickness on the short sides (use a multiple of your extrusion width)
socket_wall = 2.0;
// Extra stem thickness on the long sides (the original stem is an ellipse 23.7 x 33.4)
stem_extra_b = 2.0;
// Outer shape of the stem: "rounded" = uniform wall (best for TPU), "ellipse" = like the original (thin ~1 mm corners)
stem_shape = "rounded"; // [rounded, ellipse]

/* [Cup] */
// Cup wall thickness (1.6 = 4 x 0.4 mm). Original ~2.1
cup_wall = 1.6;
// Height from stem top to rim centre (0 = 23.2 * scale)
cup_h = 0;
// Radius where the bowl leaves the stem (0 = stem half-width)
cup_base_r = 0;
// Rim tilt in degrees (the -X side of the rim is higher = deeper cup)
rim_tilt = 16;
// Non-planar rim modulation measured on the original (1 = as original, 0 = flat tilted rim)
rim_wave = 1;
// Bowl flare: 1 = straight cone, larger = rounder bowl (original ~1.8)
cup_flare_power = 1.8;
// Diameter of the rounded bead on the rim (>= cup_wall)
lip_d = 3.2;

/* [Output] */
part = "mask"; // [mask, template]
// Cut the model in half to inspect the wall
show_section = false;
// Points around the circumference
segments = 72; // [36:4:180]
// Rings along the cup wall
cup_rings = 24; // [8:60]
// Rings around the rim bead
lip_rings = 10; // [4:24]

/* [Hidden] */
// Plan-view outer radius of the original rim, every 5 deg from 0 (shallow +X side) to 180 (deep -X side), mirrored.
RIM_REF = [23.52, 23.57, 23.66, 23.81, 23.97, 24.11, 24.19, 24.19, 24.08, 23.89, 23.67, 23.39, 23.21,
           23.10, 23.08, 23.15, 23.33, 23.64, 24.01, 24.48, 24.95, 25.18, 24.94, 24.20, 23.39, 22.86,
           22.55, 22.39, 22.34, 22.40, 22.54, 22.76, 23.04, 23.32, 23.58, 23.77, 23.84];
// Height of the original rim relative to a flat tilted plane, every 10 deg from 0 to 180, mirrored.
WAVE_REF = [0, -0.1, -0.72, -1.88, -2.07, -1.8, -1.37, -0.72, -0.02, 0.78, 1.54, 1.47, 1.06, 0.79, 0.56, 0.32, 0.13, 0.02, 0];
REF_RIM_L = RIM_REF[0] + RIM_REF[len(RIM_REF) - 1];   // 47.36
REF_RIM_W = 2 * max(RIM_REF);                          // 50.36
REF_CUP_H = 23.2;                                      // original stem top -> rim centre

// ---------------------------------------------------------------- derived
face_scale = face_scale_override > 0 ? face_scale_override : pow(cat_weight_kg / reference_weight_kg, 1 / 3);
sx = rim_length > 0 ? rim_length / REF_RIM_L : face_scale;
sy = rim_width  > 0 ? rim_width  / REF_RIM_W : face_scale;
s_avg = (sx + sy) / 2;
cup_height = cup_h > 0 ? cup_h : REF_CUP_H * s_avg;
cl = socket_clearance / 2;
mouth_a = mouth_h / 2 + cl;                 // socket half size along X
mouth_b = mouth_w / 2 + cl;                 // socket half size along Y
stem_a = mouth_a + socket_wall;             // stem half size along X
stem_b = mouth_b + socket_wall + stem_extra_b;
base_r = cup_base_r > 0 ? cup_base_r : stem_a;
tilt = tan(rim_tilt);
lip_r = max(lip_d, cup_wall) / 2;
thetas = [for (j = [0 : segments - 1]) 360 * j / segments];

// ---------------------------------------------------------------- 2D helpers (radius as a function of azimuth t in degrees)
function fold180(t) = let(a = ((t % 360) + 360) % 360) a > 180 ? 360 - a : a;
function tab_lerp(tab, step, t) =
    let(a = fold180(t), i = floor(a / step), f = a / step - i, n = len(tab))
    i >= n - 1 ? tab[n - 1] : tab[i] * (1 - f) + tab[i + 1] * f;
function ellipse_r(a, b, t) = 1 / sqrt(pow(cos(t) / a, 2) + pow(sin(t) / b, 2));
// rounded rectangle, half sizes a (X) and b (Y), corner radius rc0
function rrect_r(a, b, rc0, t) =
    let(rc = min(rc0, a, b), ux = abs(cos(t)), uy = abs(sin(t)), cx = a - rc, cy = b - rc,
        tx = ux > 1e-9 ? a / ux : 1e9, ty = uy > 1e-9 ? b / uy : 1e9,
        tm = min(tx, ty), px = tm * ux, py = tm * uy)
    (px > cx + 1e-9 && py > cy + 1e-9)
        ? let(uc = ux * cx + uy * cy) uc + sqrt(max(uc * uc - (cx * cx + cy * cy) + rc * rc, 0))
        : tm;

// ---------------------------------------------------------------- mask surface functions
// outer radius of the rim (plan view), anisotropically scaled original outline
function rim_r(t) =
    let(tp = atan2(sin(t) / sy, cos(t) / sx), rp = tab_lerp(RIM_REF, 5, tp))
    rp * sqrt(pow(sx * cos(tp), 2) + pow(sy * sin(tp), 2));
function wave(t) = rim_wave * s_avg * tab_lerp(WAVE_REF, 10, t);
// height of the rim (bead centre line) at azimuth t
function z_rim(t) = stem_h + cup_height - tilt * rim_r(t) * cos(t) + wave(t);
function socket_in_r(t, z) =
    let(shrink = socket_taper_depth > 0 ? socket_taper / 2 * min(z, socket_taper_depth) / socket_taper_depth : 0)
    rrect_r(mouth_a - shrink, mouth_b - shrink, mouth_corner_r, t);
function stem_out_r(t) = stem_shape == "ellipse"
    ? ellipse_r(stem_a, stem_b, t)
    : rrect_r(stem_a, stem_b, mouth_corner_r + socket_wall, t);
function ease(v)  = 1 - pow(1 - v, cup_flare_power);
function dease(v) = cup_flare_power * pow(1 - v, cup_flare_power - 1);
function cup_H(t) = z_rim(t) - stem_h;
function bowl_out(t, v) = base_r + (rim_r(t) - base_r) * ease(v);
// radial wall thickness that gives a constant thickness normal to the sloped wall
function t_rad(t, v) = cup_wall * sqrt(1 + pow((rim_r(t) - base_r) * dease(v) / cup_H(t), 2));
function r_out(t, v) = max(stem_out_r(t), bowl_out(t, v));
function r_in(t, v)  = max(socket_in_r(t, stem_h), bowl_out(t, v) - t_rad(t, v));
function zc(t, v) = stem_h + v * cup_H(t);

// ---------------------------------------------------------------- rings
function ring(rs, zs) = [for (j = [0 : segments - 1]) [rs[j] * cos(thetas[j]), rs[j] * sin(thetas[j]), zs[j]]];

outer_rings = concat(
    [ring([for (t = thetas) stem_out_r(t)], [for (t = thetas) 0])],
    [ring([for (t = thetas) stem_out_r(t)], [for (t = thetas) stem_h])],
    [for (i = [0 : cup_rings]) let(v = i / cup_rings)
        ring([for (t = thetas) r_out(t, v)], [for (t = thetas) zc(t, v)])]);

// bead: circle of radius lip_r centred on the wall mid-line, raised so it meets both wall faces tangentially
phi0 = acos((cup_wall / 2) / lip_r);
lip_zc = sqrt(lip_r * lip_r - pow(cup_wall / 2, 2));
bead_rings = [for (i = [0 : lip_rings]) let(phi = -phi0 + (180 + 2 * phi0) * i / lip_rings)
    ring([for (t = thetas) rim_r(t) - cup_wall / 2 + lip_r * cos(phi)],
         [for (t = thetas) z_rim(t) + lip_zc + lip_r * sin(phi)])];

inner_rings = concat(
    [for (i = [0 : cup_rings]) let(v = 1 - i / cup_rings)
        ring([for (t = thetas) r_in(t, v)], [for (t = thetas) zc(t, v)])],
    [for (z = [stem_h, min(socket_taper_depth, stem_h), 0])
        ring([for (t = thetas) socket_in_r(t, z)], [for (t = thetas) z])]);

// drop consecutive duplicate rings (they occur where shapes coincide) so no degenerate faces are produced
function ring_eq(A, B) = max([for (j = [0 : len(A) - 1]) norm(A[j] - B[j])]) < 1e-6;
loop0 = concat(outer_rings, bead_rings, inner_rings);
loop1 = [for (i = [0 : len(loop0) - 1]) if (i == 0 || !ring_eq(loop0[i], loop0[i - 1])) loop0[i]];
loop  = ring_eq(loop1[len(loop1) - 1], loop1[0]) ? [for (i = [0 : len(loop1) - 2]) loop1[i]] : loop1;

M = len(loop);
N = segments;
mask_points = [for (r = loop) each r];
// faces: every pair of consecutive rings (the loop closes on itself) -> two triangles per quad, clockwise seen from outside
mask_faces = [for (i = [0 : M - 1], j = [0 : N - 1])
    let(i2 = (i + 1) % M, a0 = i * N + j, a1 = i * N + (j + 1) % N, b0 = i2 * N + j, b1 = i2 * N + (j + 1) % N)
    each [[a0, b1, a1], [a0, b0, b1]]];

// ---------------------------------------------------------------- checks + info
min_gap = min([for (t = thetas) rim_r(t) - stem_out_r(t)]);
assert(cup_flare_power >= 1, "cup_flare_power must be >= 1");
assert(min_gap > cup_wall + 0.5, str("Rim outline is too small for the stem (gap ", min_gap,
       " mm). Increase cat size / rim_length / rim_width or reduce the socket."));
min_stem_wall = min([for (t = thetas) stem_out_r(t) - socket_in_r(t, 0)]);
assert(min_stem_wall > 0.8, str("Stem wall too thin (", min_stem_wall,
       " mm): increase socket_wall / stem_extra_b, use stem_shape = \"rounded\" or reduce mouth_corner_r."));
if (min_stem_wall < 1.2) echo(str("WARNING: thinnest stem wall is only ", min_stem_wall, " mm (at the socket corners)"));

rim_len_out = rim_r(0) + rim_r(180);
rim_wid_out = 2 * max([for (t = thetas) rim_r(t) * sin(t)]);
echo(str("face scale = ", face_scale, "  (cat ", cat_weight_kg, " kg vs reference ", reference_weight_kg, " kg)"));
echo(str("rim outline (outer): ", rim_len_out, " x ", rim_wid_out, " mm;  cup height at centre ", cup_height,
         " mm;  total height ", max([for (t = thetas) z_rim(t)]) + lip_zc + lip_r, " mm"));
echo(str("socket opening: ", 2 * mouth_a, " x ", 2 * mouth_b, " mm tapering to ",
         2 * mouth_a - socket_taper, " x ", 2 * mouth_b - socket_taper, " mm at ", socket_taper_depth, " mm depth"));

// ---------------------------------------------------------------- modules
module cat_face_mask() {
    polyhedron(points = mask_points, faces = mask_faces, convexity = 10);
}

// 1:1 paper template: outer rim outline as a ring of the wall thickness, the stem outline for orientation,
// labels for the deep (chin, -X) and shallow (nose, +X) sides and a 50 mm scale bar to check the print scale
module rim_template() {
    font = "Liberation Sans";
    difference() {
        polygon([for (t = thetas) rim_r(t) * [cos(t), sin(t)]]);
        polygon([for (t = thetas) (rim_r(t) - cup_wall) * [cos(t), sin(t)]]);
    }
    difference() {
        polygon([for (t = thetas) stem_out_r(t) * [cos(t), sin(t)]]);
        polygon([for (t = thetas) (stem_out_r(t) - 0.5) * [cos(t), sin(t)]]);
    }
    translate([-rim_r(180) - 2, 0]) text("chin", size = 3, font = font, halign = "right", valign = "center");
    translate([rim_r(0) + 2, 0]) text("nose", size = 3, font = font, halign = "left", valign = "center");
    sized_by_weight = rim_length == 0 && rim_width == 0 && face_scale_override == 0;
    translate([0, rim_wid_out / 2 + 9])
        text(sized_by_weight ? str("cat face mask, ", cat_weight_kg, " kg cat") : "cat face mask",
             size = 3, font = font, halign = "center");
    translate([0, rim_wid_out / 2 + 4])
        text(str("rim ", round(10 * rim_len_out) / 10, " x ", round(10 * rim_wid_out) / 10, " mm"),
             size = 3, font = font, halign = "center");
    translate([0, -rim_wid_out / 2 - 7]) {
        square([50, 0.5], center = true);
        for (x = [-25, 25]) translate([x, 0]) square([0.5, 3], center = true);
        translate([0, -6]) text("50 mm: check with a ruler", size = 3, font = font, halign = "center");
    }
}

if (part == "template") {
    rim_template();
} else if (show_section) {
    difference() {
        cat_face_mask();
        translate([-150, 0, -1]) cube(300);
    }
} else {
    cat_face_mask();
}
