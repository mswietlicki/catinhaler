// =====================================================================
//  Round Cushion Inhaler Mask  -  parametric OpenSCAD version
// =====================================================================
//  A parametric remake of the static design "inhalateur2.stl": a round
//  mask cup with a hollow rolled lip (soft cushion when printed in TPU)
//  and a straight socket that pushes directly onto the mouthpiece of a
//  pMDI inhaler (Ventolin / salbutamol type).
//
//  Measured from the original: socket OD 33 mm x 15 mm tall, mouthpiece
//  hole 24 x 17.5 mm straight stadium, cup flaring to 44 mm OD over ~18 mm,
//  lip rolled inwards (hollow ~5 mm, wall ~2 mm), total height ~38 mm.
//  The socket defaults are set to the same mouthpiece values as the cat face
//  mask and the holding chamber (25.4 x 19.6, corner 7, 4 mm wedge taper) so
//  the three files form one kit. For the original's hole use mouth_w = 24,
//  mouth_h = 17.5, mouth_corner_r = 8.75, socket_taper = 0.
//
//  HOW TO USE
//    1. Set cat_weight_kg (3.3 kg -> scale 0.90 of the original) or set
//       rim_d directly (outer diameter of the cup at the lip).
//    2. Measure the inhaler mouthpiece and set mouth_w / mouth_h.
//    3. part = "mask", F6 render, export STL.
//    part = "profile" shows the 2D (r,z) cross-section that is revolved.
//
//  PRINTING (TPU, 0.4 mm nozzle)
//    - Print socket down, rim up, no supports.
//    - cup_wall 1.6 mm = 4 perimeters; set >= 4 perimeters in the slicer.
//    - The rolled lip encloses a hollow ring: its roof is bridged by the
//      slicer (span ~5 mm). The inside will be rough but it is invisible
//      and the hollow is what makes the lip soft.  If your printer does
//      not bridge well in TPU use lip_style = "bead" (solid round bead).
//    - 0.2 mm layers, slow (20-30 mm/s), fan on.
//    - TPU grips: start with socket_clearance 0; add socket_taper 2-3 for
//      a wedge fit if the mouthpiece is loose.
// =====================================================================

/* [Cat size] */
// Your cat's weight. Linear size scales with (weight / reference_weight)^(1/3).
cat_weight_kg = 3.3;
// Weight of the cat the original design is assumed to fit.
reference_weight_kg = 4.5;
// Force the scale (0 = compute from weight). 1 = exact size of the original.
face_scale_override = 0;
// Outer diameter of the cup at the top of the wall in mm (0 = 44 * scale)
rim_d = 0;

/* [Inhaler socket] */
// Mouthpiece long outer dimension (mm) -> hole along X
mouth_w = 25.4;
// Mouthpiece short outer dimension (mm) -> hole along Y
mouth_h = 19.6;
// Corner radius of the mouthpiece outline (min(w,h)/2 gives a stadium). Original 8.75 (stadium)
mouth_corner_r = 7;
// Extra clearance added to the hole (TPU 0, PLA 0.3)
socket_clearance = 0;
// Total shrink of the hole from bottom to top of the socket (wedge fit). Original 0 (straight hole)
socket_taper = 4;
// Socket outer diameter
socket_od = 33;
// Socket height
socket_h = 15;

/* [Cup] */
// Cup wall thickness (1.6 = 4 x 0.4 mm). Original ~2.2
cup_wall = 1.6;
// Height from socket top to start of the lip (0 = 18.4 * scale)
cup_h = 0;
// Bowl flare: 1 = straight cone, larger = rounder (original ~2)
cup_flare_power = 2;

/* [Lip] */
lip_style = "rolled"; // [rolled, bead]
// Radius of the rolled lip centre line (hollow diameter = 2*lip_r - lip wall)
lip_r = 3.4;
// Wall thickness of the rolled lip (0 = cup_wall)
lip_wall = 0;
// How far the lip curls inwards (deg). 260 = over the top and down inside.
lip_curl_deg = 260; // [180:10:300]
// Angle (from vertical) of the strut that closes the hollow back to the wall
lip_root_angle = 40; // [20:60]
// Diameter of the solid bead when lip_style = "bead"
lip_bead_d = 4;

/* [Output] */
part = "mask"; // [mask, profile]
// Cut the model in half to inspect the wall
show_section = false;
// Segments around the circumference
$fn = 96;
// Points along the cup wall
cup_steps = 24;
// Points along the rolled lip
lip_steps = 24;

/* [Hidden] */
// preview colour of TPU parts (the STL has no colour)
TPU_COLOR = "#e0a526";
REF_RIM_D = 44.0;
REF_CUP_H = 18.4;

// ---------------------------------------------------------------- derived
sc = face_scale_override > 0 ? face_scale_override : pow(cat_weight_kg / reference_weight_kg, 1 / 3);
R1 = (rim_d > 0 ? rim_d : REF_RIM_D * sc) / 2;      // outer radius at top of the wall
cup_height = cup_h > 0 ? cup_h : REF_CUP_H * sc;
R0 = socket_od / 2;
t  = cup_wall;
lw = lip_wall > 0 ? lip_wall : cup_wall;
cl = socket_clearance / 2;
mouth_a = mouth_w / 2 + cl;
mouth_b = mouth_h / 2 + cl;

assert(cup_flare_power >= 1, "cup_flare_power must be >= 1");
assert(R1 > R0 + t, "rim_d must be larger than socket_od + 2*cup_wall");
assert(R0 - max(mouth_a, mouth_b) >= 1.5, "socket wall too thin: increase socket_od or reduce the mouthpiece size");

// ---------------------------------------------------------------- wall profile  (r, z)
function ease(v)  = 1 - pow(1 - v, cup_flare_power);
function dease(v) = cup_flare_power * pow(1 - v, cup_flare_power - 1);
function r_out(v) = R0 + (R1 - R0) * ease(v);
// radial thickness giving constant thickness normal to the sloped wall
function t_rad(v) = t * sqrt(1 + pow((R1 - R0) * dease(v) / cup_height, 2));
function r_in(v)  = r_out(v) - t_rad(v);
function zc(v)    = socket_h + v * cup_height;

wall_outer = [for (i = [0 : cup_steps]) let(v = i / cup_steps) [r_out(v), zc(v)]];
wall_inner = [for (i = [cup_steps : -1 : 0]) let(v = i / cup_steps) [r_in(v), zc(v)]];

// ---------------------------------------------------------------- lip
rc = R1 - t / 2;          // wall centre line at the top
z1 = zc(1);
// rolled lip: arc tangent to the wall at the top, curling inwards, then a strut back to the wall
arc = [for (i = [0 : lip_steps]) let(a = lip_curl_deg * i / lip_steps) [rc - lip_r + lip_r * cos(a), z1 + lip_r * sin(a)]];
arc_end = arc[lip_steps];
// first inner-wall point (from the top) that the strut line reaches
strut_hits = [for (i = [0 : cup_steps]) let(v = 1 - i / cup_steps, p = [r_in(v), zc(v)])
    if (p[1] < arc_end[1] && p[0] <= arc_end[0] + (arc_end[1] - p[1]) * tan(lip_root_angle)) i];
strut_i = len(strut_hits) > 0 ? min(strut_hits) : cup_steps;
strut_v = 1 - strut_i / cup_steps;
strut_end = [r_in(strut_v) + t / 2, zc(strut_v)];
lip_path = concat(arc, [strut_end]);

module sheet(path, w) {
    for (i = [0 : len(path) - 2]) hull() {
        translate(path[i]) circle(d = w);
        translate(path[i + 1]) circle(d = w);
    }
}

module profile2d() {
    // socket (solid; the mouthpiece hole is cut later) and floor
    square([R0, socket_h]);
    // cup wall
    polygon(concat(wall_outer, wall_inner));
    // lip
    if (lip_style == "rolled") {
        sheet(lip_path, lw);
    } else {
        br = max(lip_bead_d, t) / 2;
        translate([rc, z1 + sqrt(br * br - t * t / 4)]) circle(r = br);
    }
}

// ---------------------------------------------------------------- mouthpiece hole (stadium / rounded rectangle, optional taper)
// (hull of four corner circles: still valid when the corner radius equals the half height, i.e. a stadium)
module rrect2d(a, b, rc0) {
    r = min(rc0, a, b);
    if (r < 0.05) {
        square([2 * a, 2 * b], center = true);
    } else {
        hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx * (a - r), sy * (b - r)]) circle(r = r);
    }
}
module mouth_hole() {
    hull() {
        translate([0, 0, -1]) linear_extrude(0.01) rrect2d(mouth_a, mouth_b, mouth_corner_r);
        translate([0, 0, socket_h + 1]) linear_extrude(0.01)
            rrect2d(mouth_a - socket_taper / 2, mouth_b - socket_taper / 2, mouth_corner_r);
    }
}

module round_mask() {
    difference() {
        rotate_extrude() profile2d();
        mouth_hole();
    }
}

// ---------------------------------------------------------------- info
echo(str("scale = ", sc, "  rim OD = ", 2 * R1, " mm  cup height = ", cup_height,
         " mm  total height = ", z1 + lip_r + lw / 2, " mm"));
echo(str("mouthpiece hole: ", 2 * mouth_a, " x ", 2 * mouth_b, " mm", socket_taper > 0 ? str(" tapering by ", socket_taper, " mm") : ""));
if (lip_style == "rolled")
    echo(str("rolled lip: hollow about ", 2 * lip_r - lw, " mm, strut joins the wall ", z1 - strut_end[1], " mm below the top"));

if (part == "profile") {
    profile2d();
} else if (show_section) {
    color(TPU_COLOR) difference() {
        round_mask();
        translate([-150, 0, -1]) cube(300);
    }
} else {
    color(TPU_COLOR) round_mask();
}
