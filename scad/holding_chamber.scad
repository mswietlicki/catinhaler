// =====================================================================
//  Small Holding Chamber (spacer) for the cat inhaler masks
// =====================================================================
//  Sits between the inhaler and one of the mask adapters:
//
//     [inhaler] -> inhaler socket | chamber body | cap + nozzle -> [mask]
//
//  - The inhaler socket follows the real Ventolin / albuterol HFA mouthpiece
//    outline: straight short ends, long sides that bulge outwards, small
//    corners.  The body is rigid, so the socket starts a little larger than
//    the mouthpiece and narrows gently; the mouthpiece seats part way in.
//  - The nozzle on the cap imitates the mouthpiece in the simpler rounded
//    rectangle the TPU mask sockets are made for, so it plugs into either
//    mask.  Use the SAME mouth_w / mouth_h / mouth_corner_r values as in
//    your mask file(s).
//  - Inhalation valve: a thin TPU flap on a grille insert.  The flap lifts
//    when the cat breathes in and closes when it breathes out, so the dose
//    waits in the chamber instead of being blown back out.
//  - Exhalation valve: a TPU umbrella valve recessed in the top of the cap,
//    next to the nozzle.  Exhaled air passes from the mask side of the flap
//    through six holes under the umbrella and lifts its rim; on inhalation
//    the umbrella is sucked flat and seals.  Without it the cat would have
//    to exhale past the mask rim and would re-breathe the mask volume.
//  - Two pieces (body + cap, press fit) so it can be opened for cleaning
//    and the valves can be installed.  one_piece = true fuses them (no valves).
//
//  PARTS  (part = "all" lays everything out for printing)
//    body      - socket + chamber tube, print socket down, no supports
//    cap       - skirt + lid + nozzle, print skirt down, no supports
//    insert    - inhalation valve seat disc with grille and hinge slot, flat
//    flap      - inhalation flap in TPU, print disc down (0.6 mm = 3 layers)
//                with the hinge tab standing up at 90 deg
//    umbrella  - exhalation umbrella, print disc down, stem up, in TPU
//    socket_test - just the inhaler socket end of the body, a quick print
//                to try the inhaler fit before printing the whole body
//  ASSEMBLY: push the flap's tab, barb first, down through the slot of the
//    insert and pull it from below until the barb pops through and the
//    disc lies flat on the insert (that face goes towards the nozzle).
//    Drop the insert into the cap skirt, flap towards the nozzle, and push
//    it up to the stop.  Push the umbrella stem into the small hole in the
//    pocket on top of the cap until the bulb clicks into the pocket under
//    the seat.  Push the cap skirt into the body: the crush ribs on the
//    skirt hold it.
//
//  MATERIAL: body, cap and insert are best in a rigid filament (PETG/PLA)
//    so the chamber keeps its shape; TPU works too with wall = 2 mm but
//    is squeezable.  The flap must be TPU.  Non-antistatic plastic holds
//    charge that steals aerosol: wash in diluted dish soap and air dry
//    without rinsing/wiping (standard spacer advice).
//
//  SIZE: default 40 mm x 80 mm tube, about 105 ml internal volume, in
//    the range of commercial cat chambers; a 3.3 kg cat empties it in a
//    few breaths.  Change chamber_d / chamber_len freely; the volume is
//    echoed in the console.
// =====================================================================

/* [Inhaler socket  (your inhaler's mouthpiece)] */
// Defaults: GSK Ventolin HFA / Evohaler actuator, fitted to two sockets that were made for it
// (city17's "Bottle Adapter for Cat Asthma Inhaler", Printables 848067, and bens' "Vase Mode
// Ventolin Inhaler Spacer", NIH 3D 3DPX-018151) and to photos of the mouthpiece and its cap.
// Mouthpiece long outer width (mm) -> along Y
inhaler_w = 25.4;
// Mouthpiece short outer height at the middle of the long sides, where they bulge most (mm) -> along X
inhaler_h = 19.6;
// Short outer height at the ends of the long sides, next to the corners (mm); = inhaler_h for flat sides
inhaler_end_h = 12;
// Corner radius of the mouthpiece outline
inhaler_corner_r = 2;
// Socket mouth minus mouthpiece size, on the width and the height (mm): + = the mouthpiece goes in deeper
inhaler_fit = 0.6;
// Total shrink of the socket over socket_taper_depth: the mouthpiece wedges where the socket reaches its size
socket_taper = 2;
socket_taper_depth = 15;
// Total depth of the inhaler socket
socket_depth = 18;
// 45 deg chamfer at the socket mouth that guides the mouthpiece in (also takes the elephant's foot of the first layers)
socket_lead_in = 1;

/* [Mask connector shape  (copy from your mask file)] */
// Long outer dimension of the mask socket the nozzle plugs into (mm) -> along Y
mouth_w = 25.4;
// Short outer dimension (mm) -> along X
mouth_h = 19.6;
// Corner radius of the mask socket outline
mouth_corner_r = 7;

/* [Chamber] */
// Outer diameter of the chamber tube
chamber_d = 40;
// Length of the cylindrical part
chamber_len = 80;
// Wall thickness of body and cap (2.0 = 5 x 0.4 mm)
wall = 2.0;
// Length of the cone between the socket and the tube
inlet_cone_len = 12;

/* [Mask connector (nozzle)] */
// Length of the nozzle that enters the mask socket (= socket_taper_depth of the mask for a full-length fit)
nozzle_len = 15;
// Total shrink of the nozzle from base to tip (= socket_taper of the mask so the two cones mate along their length)
nozzle_taper = 4;
// Wall thickness of the nozzle (1.6 = 4 x 0.4 mm)
nozzle_wall = 1.6;
// Make the nozzle bigger (+) or smaller (-) than the mouthpiece size, so it stretches the TPU mask socket and grips (0 = exactly the mouthpiece)
nozzle_oversize = 0.4;
// Length of the cone between the chamber diameter and the nozzle (longer = gentler internal overhang)
head_cone_len = 10;

/* [Inhalation valve] */
valve = true;
// Diameter of the valve opening in the insert
valve_d = 16;
// Width of the grille bars across the opening
grille_w = 1.6;
// Thickness of the insert disc
insert_t = 1.6;
// Flap thickness (TPU, 0.6 = 3 layers of 0.2)
flap_t = 0.6;
// How far the flap overlaps the opening all round
flap_overlap = 2;
// Width of the flap hinge tab
tab_w = 6;
// Thickness of the flap hinge tab, printed standing up at the disc edge (0.8 = 2 lines of 0.4 mm)
tab_t = 0.8;
// Diametral fit of the insert in the cap bore: positive = looser, negative = press fit
insert_clearance = -0.1;

/* [Exhalation valve] */
exhale_valve = true;
// Umbrella disc diameter
umbrella_d = 10;
// Umbrella thickness (TPU, 0.4 = 2 layers of 0.2)
umbrella_t = 0.4;
// Number of exhalation holes under the umbrella
exhale_holes = 6;
// Diameter of the exhalation holes
exhale_hole_d = 1.8;
// Lid diameter of the cap when the exhalation valve is fitted (needs room beside the nozzle)
head_d = 49;
// Thickness of the lid plate above the ceiling cone that carries the valve seat
lid_t = 3;
// Depth of the recess that holds the umbrella
pocket_depth = 4;

/* [Cap joint] */
// Length of the cap skirt that enters the body
skirt_len = 10;
// Radial clearance between skirt and body (TPU 0, PETG/PLA 0.15-0.2)
skirt_clearance = 0.15;
// Number of crush ribs on the skirt that grip the body (0 = plain skirt)
skirt_ribs = 6;
// How far the ribs reach into the body wall, radially: +0.1 if the cap is still loose, -0.1 if it is too hard to push in
skirt_rib_interference = 0.25;

/* [Output] */
part = "all"; // [all, body, cap, insert, flap, umbrella, socket_test, assembly, exploded]
// Fuse body and cap into one print (no valve possible)
one_piece = false;
// Cut the model in half to inspect
show_section = false;
$fn = 96;

/* [Hidden] */
// preview colour of the TPU parts (flap, umbrella); the STL has no colour
TPU_COLOR = "#e0a526";

// ---------------------------------------------------------------- derived
sd = inhaler_fit / 2;                  // socket mouth outline = mouthpiece outline offset outwards by this
ma = inhaler_h / 2 + sd;               // socket mouth half size along X (middle of the long side)
mb = inhaler_w / 2 + sd;               // socket mouth half size along Y
sh = socket_taper / 2;                 // shrink per side at full taper depth
R  = chamber_d / 2;
Ri = R - wall;
z_sock = socket_depth;
z_cone = z_sock + inlet_cone_len;
z_top  = z_cone + chamber_len;         // body height

na = mouth_h / 2 + nozzle_oversize / 2;   // nozzle base half sizes (= mask socket)
nb = mouth_w / 2 + nozzle_oversize / 2;
nt = nozzle_taper / 2;                 // nozzle shrink per side at the tip
nrc = mouth_corner_r;

fused = one_piece;
skirt_h  = fused ? 0 : skirt_len;
skirt_od = fused ? chamber_d : 2 * Ri - 2 * skirt_clearance;
bore_d   = fused ? 2 * Ri : skirt_od - 2 * wall;
flare_h  = fused ? 0 : (chamber_d - skirt_od) / 2;          // 45 deg flare from skirt to full diameter
rib_r    = 0.8;                                              // crush ribs: rounded, narrow enough to deform instead of the body
rib_reach = Ri + skirt_rib_interference;                     // radius the rib crests reach
rib_lead = 2;                                                // the ribs ramp up over the first 2 mm of the skirt
seat_len = valve ? insert_t + flap_t + 1 : 1;               // room for insert + flap below the ceiling
z_c = skirt_h + max(flare_h, seat_len);                      // start of the head cone (ceiling)
z_n = z_c + head_cone_len;                                   // top of the ceiling cone (nozzle channel starts)
ex_on   = exhale_valve && !one_piece;
z_lid = z_n + (ex_on ? lid_t : 0);                           // top of the lid = nozzle base
cap_h = z_lid + nozzle_len;

flap_d = valve_d + 2 * flap_overlap;
hinge_r = flap_d / 2;                  // hinge slot (and the flap's tab) sit at the flap's edge
slot_w = tab_w + 0.4;
slot_t = tab_t + 0.4;
barb = 0.8;                            // the barb at the end of the tab is this much wider than the tab on each side
barb_z = flap_t + insert_t + 0.2;      // tab length from the bed to the barb: through the insert plus 0.2 mm play
tab_len = barb_z + barb + 0.4 + 3;     // 45 deg barb shoulder, 0.4 mm flat, 3 mm lead-in point

// exhalation valve geometry (on the +X side of the lid, where the nozzle is narrowest)
pocket_d = umbrella_d + 2;                       // recess that holds the umbrella
r_ex    = na + 0.8 + pocket_d / 2;               // pocket centre radius
seat_z  = z_lid - pocket_depth;                  // pocket floor = valve seat (above the ceiling cone)
seat_t  = 2;                                     // seat thickness the stem passes through
stem_hole_d = 2.4;
stem_d = 2.2;
bulb_d = 3.4;
bulb_pocket_d = 3.8;                             // blind pocket under the seat that the bulb snaps into
bulb_pocket_h = 3;
stem_len = seat_t + 0.3;                         // umbrella stem length (disc to bulb)
hole_circle_r = umbrella_d / 2 - exhale_hole_d / 2 - 1.2;
lid_d = ex_on ? head_d : chamber_d;

assert(!(one_piece && valve), "one_piece = true cannot hold a valve (no access to install it); set valve = false");
assert(bore_d > flap_d + 2, str("Chamber too narrow for the valve: bore ", bore_d, " mm, flap ", flap_d, " mm. Increase chamber_d or reduce valve_d."));
assert(Ri > max(ma, mb) - sh + 1, "chamber_d too small for the mouthpiece socket");
assert(inhaler_end_h <= inhaler_h && inhaler_end_h > 2 * inhaler_corner_r, "inhaler_end_h must lie between 2 x inhaler_corner_r and inhaler_h");
assert(sh < sd + inhaler_corner_r + inhaler_end_h / 2 - 1, "socket_taper too large for this mouthpiece");
assert(nt < min(na, nb) - nozzle_wall - 2, "nozzle_taper too large for the nozzle size");
assert(!ex_on || r_ex + pocket_d / 2 + 1.2 <= lid_d / 2, str("head_d too small for the exhalation valve: needs at least ", 2 * (r_ex + pocket_d / 2 + 1.2), " mm"));
assert(!ex_on || seat_z - seat_t - bulb_pocket_h > z_c + 1, "exhalation pocket too deep for this head: reduce pocket_depth or increase head_cone_len");

// ---------------------------------------------------------------- lofts (polyhedron based: no CGAL hull, fast and robust)
segs = max(24, $fn);
thetas = [for (j = [0 : segs - 1]) 360 * j / segs];
// radius of a rounded rectangle (half sizes a along X, b along Y, corner radius rc0) in direction t (deg)
function rrect_r(a, b, rc0, t) =
    let(rc = min(rc0, a, b), ux = abs(cos(t)), uy = abs(sin(t)), cx = a - rc, cy = b - rc,
        tx = ux > 1e-9 ? a / ux : 1e9, ty = uy > 1e-9 ? b / uy : 1e9,
        tm = min(tx, ty), px = tm * ux, py = tm * uy)
    (px > cx + 1e-9 && py > cy + 1e-9)
        ? let(uc = ux * cx + uy * cy) uc + sqrt(max(uc * uc - (cx * cx + cy * cy) + rc * rc, 0))
        : tm;
function rr_list(a, b, rc) = [for (t = thetas) rrect_r(a, b, rc, t)];
function circ_list(d)      = [for (t = thetas) d / 2];

// Ventolin-type mouthpiece outline ("barrel"), counter-clockwise points: straight short ends at y = +-b,
// long sides are circular arcs that bulge to x = +-a at the middle and come in to x = +-ae at the ends,
// corners rounded with rc.  d offsets the whole outline outwards (+) or inwards (-): the corners grow or
// shrink with it, and once they are sharp the rest of the outline keeps shrinking.  Every outline has the
// same number of points at nearly the same angles, so two of them loft point to point.
function barrel_pts(a, b, ae, rc, d = 0) =
    let(bulge = max(a - ae, 0.01),
        Ra = (b * b + bulge * bulge) / (2 * bulge),   // arc through (a, 0) and (ae, +-b)
        cx = a - Ra,                                   // centre of the +X arc (the -X arc mirrors it)
        r  = max(rc + d, 0.1),                         // corner radius of the offset outline
        e  = r - rc - d,                               // extra shrink of the core once the corners are sharp
        kb = b - rc - e, kr = Ra - rc - e,             // core = |y| <= kb inside both arcs of radius kr
        kx = cx + sqrt(kr * kr - kb * kb),             // core corner
        ph = atan2(kb, kx - cx),                       // half angle of each arc
        na = 16, nc = 8, ns = 8, y = kb + r)
    concat([for (i = [0 : na - 1]) let(t = -ph + 2 * ph * i / na)       [ cx + (kr + r) * cos(t), (kr + r) * sin(t)]],
           [for (i = [0 : nc - 1]) let(t = ph + (90 - ph) * i / nc)       [ kx + r * cos(t),  kb + r * sin(t)]],
           [for (i = [0 : ns - 1]) [kx - 2 * kx * i / ns, y]],
           [for (i = [0 : nc - 1]) let(t = 90 + (90 - ph) * i / nc)       [-kx + r * cos(t),  kb + r * sin(t)]],
           [for (i = [0 : na - 1]) let(t = 180 - ph + 2 * ph * i / na)  [-cx + (kr + r) * cos(t), (kr + r) * sin(t)]],
           [for (i = [0 : nc - 1]) let(t = 180 + ph + (90 - ph) * i / nc) [-kx + r * cos(t), -kb + r * sin(t)]],
           [for (i = [0 : ns - 1]) [-kx + 2 * kx * i / ns, -y]],
           [for (i = [0 : nc - 1]) let(t = 270 + (90 - ph) * i / nc)      [ kx + r * cos(t), -kb + r * sin(t)]]);
// circle of diameter dc sampled at the angles of the points of outline p, to loft p into
function circle_like(p, dc) = [for (q = p) dc / 2 * q / norm(q)];
function sum(v, i = 0) = i >= len(v) ? 0 : v[i] + sum(v, i + 1);
function poly_area(p) = abs(sum([for (i = [0 : len(p) - 1]) let(q = p[(i + 1) % len(p)]) p[i][0] * q[1] - p[i][1] * q[0]])) / 2;
// the inhaler mouthpiece outline offset by d
function socket_pts(d) = barrel_pts(inhaler_h / 2, inhaler_w / 2, inhaler_end_h / 2, inhaler_corner_r, d);
inhaler_outline = socket_pts(0);       // the mouthpiece itself (for the diagrams)

// closed solid between outline p0 at height z0 and outline p1 at height z1 (2D point lists, same length,
// point j of one matching point j of the other)
module loft_xy(p0, p1, z0, z1) {
    n = len(p0);
    pts = concat([for (q = p0) [q[0], q[1], z0]], [for (q = p1) [q[0], q[1], z1]]);
    faces = concat([[for (j = [0 : n - 1]) j]],
                   [[for (j = [n - 1 : -1 : 0]) n + j]],
                   [for (j = [0 : n - 1]) [j, n + j, n + (j + 1) % n, (j + 1) % n]]);
    polyhedron(points = pts, faces = faces, convexity = 4);
}
// closed solid between outline r0 at height z0 and outline r1 at height z1 (both convex, sampled at the same angles)
module loft(r0, r1, z0, z1) {
    loft_xy([for (j = [0 : len(thetas) - 1]) r0[j] * [cos(thetas[j]), sin(thetas[j])]],
            [for (j = [0 : len(thetas) - 1]) r1[j] * [cos(thetas[j]), sin(thetas[j])]], z0, z1);
}
module rrect_taper(a0, b0, a1, b1, rc, z0, z1)   { loft(rr_list(a0, b0, rc), rr_list(a1, b1, rc), z0, z1); }
module loft_rrect_circle(a, b, rc, d, z0, z1)    { loft(rr_list(a, b, rc), circ_list(d), z0, z1); }
module loft_circle_rrect(d, a, b, rc, z0, z1)    { loft(circ_list(d), rr_list(a, b, rc), z0, z1); }
// 2D rounded rectangle (hull of corner circles, valid up to a full stadium)
module rrect2d(a, b, rc0) {
    r = min(rc0, a, b);
    if (r < 0.05) square([2 * a, 2 * b], center = true);
    else hull() for (sx = [-1, 1], sy = [-1, 1]) translate([sx * (a - r), sy * (b - r)]) circle(r = r);
}

// ---------------------------------------------------------------- body
module body() {
    difference() {
        union() {
            socket_end_outside();
            translate([0, 0, z_cone]) cylinder(d = chamber_d, h = chamber_len);
        }
        socket_end_inside();
        translate([0, 0, z_cone - 0.01]) cylinder(d = 2 * Ri, h = chamber_len + 1);
    }
}
module socket_end_outside() {
    p_out = socket_pts(sd + wall);
    loft_xy(p_out, p_out, 0, z_sock + 0.01);
    loft_xy(p_out, circle_like(p_out, chamber_d), z_sock, z_cone + 0.01);
}
// inhaler socket: lead-in chamfer, gentle wedge taper, straight to the inlet cone, inlet cone
module socket_end_inside() {
    lead = min(socket_lead_in, socket_taper_depth / 2);
    p_mouth = socket_pts(sd);
    p_bot = socket_pts(sd - sh);
    p_lead = socket_pts(sd - sh * lead / socket_taper_depth);        // the taper outline at the bottom of the chamfer
    loft_xy(socket_pts(sd + lead), socket_pts(sd + lead), -1, 0.01);
    loft_xy(socket_pts(sd + lead), p_lead, 0, lead);
    loft_xy(p_mouth, p_bot, 0, socket_taper_depth);
    loft_xy(p_bot, p_bot, socket_taper_depth - 0.01, z_sock + 0.02);
    loft_xy(p_bot, circle_like(p_bot, 2 * Ri), z_sock, z_cone + 0.02);
}
// the socket end of the body alone, cut 3 mm into the inlet cone: print it to try the inhaler fit
module socket_test() {
    difference() {
        intersection() {
            socket_end_outside();
            translate([0, 0, -1]) cylinder(r = chamber_d, h = z_sock + 4);
        }
        socket_end_inside();
    }
}

// ---------------------------------------------------------------- cap  (print orientation = assembled orientation: skirt down, nozzle up)
module cap() {
    difference() {
        union() {
            if (!fused) {
                cylinder(d = skirt_od, h = skirt_h + 0.01);
                if (skirt_ribs > 0) skirt_crush_ribs();
                translate([0, 0, skirt_h]) cylinder(d1 = skirt_od, d2 = chamber_d, h = flare_h);
            }
            translate([0, 0, skirt_h + flare_h - 0.01]) cylinder(d = chamber_d, h = z_c - skirt_h - flare_h + 0.02);
            if (ex_on) {
                // flat-topped lid with room for the exhalation valve beside the nozzle
                lid_flare = (lid_d - chamber_d) / 2;
                translate([0, 0, z_c - 0.01]) cylinder(d1 = chamber_d, d2 = lid_d, h = lid_flare);
                translate([0, 0, z_c + lid_flare - 0.02]) cylinder(d = lid_d, h = z_lid - z_c - lid_flare + 0.02);
            } else {
                loft_circle_rrect(chamber_d, na, nb, nrc, z_c, z_n);
            }
            rrect_taper(na, nb, na - nt, nb - nt, nrc, z_lid - 0.01, cap_h);
        }
        // bore (insert and flap live at its top), ceiling cone, nozzle channel
        translate([0, 0, -1]) cylinder(d = bore_d, h = z_c + 1);
        loft_circle_rrect(bore_d, na - nozzle_wall, nb - nozzle_wall, nrc - nozzle_wall, z_c - 0.01, z_n);
        rrect_taper(na - nozzle_wall, nb - nozzle_wall, na - nt - nozzle_wall, nb - nt - nozzle_wall, nrc - nozzle_wall, z_n - 0.01, cap_h + 1);
        if (ex_on) exhale_valve_cuts();
    }
}

// vertical ribs on the skirt, ramped at the tip; offset half a step so none lies in the show_section plane
module skirt_crush_ribs() {
    intersection() {
        for (i = [0 : skirt_ribs - 1]) rotate(360 * (i + 0.5) / skirt_ribs)
            translate([rib_reach - rib_r, 0, 0]) cylinder(r = rib_r, h = skirt_h, $fn = 24);
        union() {
            cylinder(r1 = skirt_od / 2, r2 = rib_reach, h = rib_lead);
            translate([0, 0, rib_lead - 0.01]) cylinder(r = rib_reach + 1, h = skirt_h);
        }
    }
}

// pocket, stem hole with bulb pocket, and angled exhalation holes for the umbrella valve
module exhale_valve_cuts() {
    translate([r_ex, 0, seat_z]) cylinder(d = pocket_d, h = pocket_depth + 1);                        // recess, open to the top
    translate([r_ex, 0, seat_z - seat_t - 0.01]) cylinder(d = stem_hole_d, h = seat_t + 1);          // stem hole through the seat
    translate([r_ex, 0, seat_z - seat_t - bulb_pocket_h]) cylinder(d = bulb_pocket_d, h = bulb_pocket_h + 0.01);  // blind pocket for the bulb
    for (i = [0 : exhale_holes - 1]) let(a = 360 * i / exhale_holes)
        translate([r_ex + hole_circle_r * cos(a), hole_circle_r * sin(a), seat_z + 1])
            rotate([0, 225, 0]) cylinder(d = exhale_hole_d, h = 14, $fn = 16);                        // 45 deg down and inwards into the vestibule
}

// exhalation umbrella: print disc down, stem up (TPU)
module umbrella() {
    cylinder(d = umbrella_d, h = umbrella_t);
    translate([0, 0, umbrella_t - 0.01]) cylinder(d = stem_d, h = stem_len + 0.01);
    translate([0, 0, umbrella_t + stem_len - 0.01]) cylinder(d1 = bulb_d, d2 = stem_d - 0.6, h = 1.6);
}

// ---------------------------------------------------------------- valve insert (print flat) and flap (TPU, disc down)
module valve_insert() {
    difference() {
        cylinder(d = bore_d - insert_clearance, h = insert_t);
        translate([0, 0, -1]) cylinder(d = valve_d, h = insert_t + 2);
        // hinge slot, tangential, centred on the flap edge
        translate([hinge_r - slot_t / 2, -slot_w / 2, -1]) cube([slot_t, slot_w, insert_t + 2]);
    }
    // grille bars (+) across the opening
    intersection() {
        cylinder(d = valve_d + 1, h = insert_t);
        union() {
            translate([0, 0, insert_t / 2]) cube([valve_d + 1, grille_w, insert_t], center = true);
            translate([0, 0, insert_t / 2]) cube([grille_w, valve_d + 1, insert_t], center = true);
        }
    }
}
// The hinge tab stands up at the disc edge, already bent 90 deg, so the disc lies flat once the tab is
// through the slot; a tab printed flat springs back and lifts the disc.  The face on the bed is the top
// face in the cap (towards the nozzle).
module valve_flap() {
    hw = tab_w / 2;
    bw = hw + barb;                     // wider than the slot: squeezes through, then holds
    tip = 1.2;
    linear_extrude(flap_t) {
        circle(d = flap_d);
        // lip that carries the tab and covers the slot when the flap is closed
        translate([hinge_r - 2, -(slot_w / 2 + 0.6)]) square([2 + slot_t / 2 + 0.6, slot_w + 1.2]);
    }
    // tab in the YZ plane, centred on the slot; every overhang of the barb is 45 deg or less
    translate([hinge_r - tab_t / 2, 0, 0]) rotate([90, 0, 90]) linear_extrude(tab_t)
        polygon([[-hw, 0], [hw, 0], [hw, barb_z], [bw, barb_z + barb], [bw, barb_z + barb + 0.4], [tip, tab_len],
                 [-tip, tab_len], [-bw, barb_z + barb + 0.4], [-bw, barb_z + barb], [-hw, barb_z]]);
}

// ---------------------------------------------------------------- assembly / layout
module assembly() {
    body();
    translate([0, 0, z_top - skirt_h]) {
        cap();
        if (valve) {
            // insert pushed up to the ceiling stop, flap lying on it (shown closed, tab down through the slot)
            translate([0, 0, z_c - insert_t]) color("silver") valve_insert();
            translate([0, 0, z_c + flap_t]) mirror([0, 0, 1]) color(TPU_COLOR) valve_flap();
        }
        if (ex_on) translate([r_ex, 0, seat_z + umbrella_t]) mirror([0, 0, 1]) color(TPU_COLOR) umbrella();
    }
}

module exploded() {
    body();
    translate([0, 0, z_top - skirt_h]) {
        if (valve) {
            translate([0, 0, z_c - insert_t + 18]) color("silver") valve_insert();
            translate([0, 0, z_c + flap_t + 31]) mirror([0, 0, 1]) color(TPU_COLOR) valve_flap();
        }
        translate([0, 0, valve ? 50 : 25]) cap();
        if (ex_on) translate([r_ex, 0, (valve ? 50 : 25) + seat_z + umbrella_t + 18]) mirror([0, 0, 1]) color(TPU_COLOR) umbrella();
    }
}

module one_piece_chamber() {
    union() {
        body();
        translate([0, 0, z_top]) cap();
    }
}

module layout() {
    if (one_piece) one_piece_chamber();
    else {
        body();
        translate([chamber_d + 12, 0, 0]) cap();
        if (valve) {
            translate([-(chamber_d / 2 + bore_d / 2 + 10), 0, 0]) valve_insert();
            translate([-(chamber_d / 2 + bore_d / 2 + 10), bore_d / 2 + flap_d / 2 + 8, 0]) color(TPU_COLOR) valve_flap();
        }
        if (ex_on) translate([-(chamber_d / 2 + bore_d / 2 + 10), -(bore_d / 2 + umbrella_d / 2 + 8), 0]) color(TPU_COLOR) umbrella();
    }
}

module selected() {
    if (part == "body")          { if (one_piece) one_piece_chamber(); else body(); }
    else if (part == "cap")      cap();
    else if (part == "insert")   valve_insert();
    else if (part == "flap")     color(TPU_COLOR) valve_flap();
    else if (part == "umbrella") color(TPU_COLOR) umbrella();
    else if (part == "socket_test") socket_test();
    else if (part == "assembly") { if (one_piece) one_piece_chamber(); else assembly(); }
    else if (part == "exploded") { if (one_piece) one_piece_chamber(); else exploded(); }
    else layout();
}

// ---------------------------------------------------------------- info
function A_rr(a, b, rc) = 4 * a * b - (4 - PI) * rc * rc;          // area of a rounded rectangle
function frustum(A1, A2, h) = h / 3 * (A1 + A2 + sqrt(A1 * A2));
A_in1 = poly_area(socket_pts(sd - sh));
A_tube = PI * Ri * Ri;
A_bore = PI * pow(bore_d / 2, 2);
A_noz  = A_rr(na - nozzle_wall, nb - nozzle_wall, nrc - nozzle_wall);
v_main = A_tube * chamber_len + frustum(A_in1, A_tube, inlet_cone_len) + A_bore * z_c + frustum(A_bore, A_noz, head_cone_len);
v_sock = socket_depth * (poly_area(socket_pts(sd)) + A_in1) / 2;
echo(str("chamber internal volume ~ ", round(v_main / 100) / 10, " ml (tube + cones + cap), plus ~", round(v_sock / 100) / 10, " ml inside the inhaler socket"));
echo(str("body height ", z_top, " mm, cap height ", cap_h, " mm, assembled length ", z_top - skirt_h + cap_h, " mm, outer diameter ", chamber_d, " mm"));
echo(str("nozzle: base ", 2 * na, " x ", 2 * nb, " mm -> tip ", 2 * (na - nt), " x ", 2 * (nb - nt), " mm over ", nozzle_len, " mm"));
echo(str("inhaler socket for a ", inhaler_w, " x ", inhaler_h, " mm mouthpiece (", inhaler_end_h, " mm at the ends): mouth ", 2 * mb, " x ", 2 * ma,
         " mm narrowing to ", 2 * (mb - sh), " x ", 2 * (ma - sh), " mm at ", socket_taper_depth, " mm deep; a mouthpiece of exactly that size seats ",
         round(10 * socket_taper_depth * min(sd / sh, 1)) / 10, " mm deep, ", round(10 * socket_taper_depth / socket_taper) / 100, " mm less per 0.1 mm larger"));
if (valve) echo(str("valve: opening ", valve_d, " mm, flap ", flap_d, " x ", flap_t, " mm with a ", tab_w, " x ", tab_t, " x ", tab_len, " mm standing tab, insert ", bore_d - insert_clearance, " mm dia in a ", bore_d, " mm bore; ceiling clearance above the flap edge ~", round(10 * (bore_d / 2 - hinge_r) / (bore_d / 2 - min(na, nb) + nozzle_wall) * head_cone_len) / 10, " mm"));
if (ex_on) echo(str("exhalation valve: umbrella ", umbrella_d, " x ", umbrella_t, " mm, ", exhale_holes, " holes of ", exhale_hole_d, " mm (", round(exhale_holes * PI * pow(exhale_hole_d / 2, 2) * 10) / 10, " mm2), lid ", lid_d, " mm"));

if (show_section) difference() { selected(); translate([-150, 0, -1]) cube(300); }
else selected();
