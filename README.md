# areocat

3D-printable, parametric (OpenSCAD) adapters for giving a cat a metered-dose inhaler (Ventolin / salbutamol type pMDI):

- **two TPU face masks** that push straight onto the inhaler mouthpiece: an anatomical *cat face* mask with a tilted rim, and a *round* mask with a soft hollow rolled lip;
- **a small valved holding chamber** (about 105 ml) that goes between the inhaler and either mask, with a TPU flap inhalation valve and a TPU umbrella exhalation valve. A valveless one-piece spacer is included as a simpler alternative.

The defaults fit a **3.3 kg cat** and a **25.4 x 19.6 mm** mouthpiece; both are parameters.

![All parts in print orientation: TPU amber, PETG blue](docs/img/print_layout.png)

> **Hobby designs, not medical devices.** Use them only with your veterinarian's guidance and dosing instructions, check every part for sharp edges before it touches your cat, and never force a mask on a struggling animal. The printed valves have not been laboratory tested.

**[Read the full manual](MANUAL.md)**: measuring, sizing, detailed print settings, assembly, fitting the mask, cleaning and troubleshooting.

## Print order

Print and test in this order, so a wrong size shows up before you have printed everything.

| # | Print | Material | Check before moving on |
|---|---|---|---|
| 1 | [`docs/cat_face_rim_template.svg`](docs/cat_face_rim_template.svg) on paper at 100 % | paper | The 50 mm bar measures 50 mm; the outline covers nose and mouth and stays below the eyes. Otherwise change `cat_weight_kg`. |
| 2 | `stl/cat_face_inhaler_mask.stl` or `stl/round_cushion_inhaler_mask.stl` | TPU | The inhaler wedges firmly into the socket. Mask plus inhaler already works without a chamber. |
| 3 | `stl/holding_chamber_body.stl`, `stl/holding_chamber_cap.stl`, `stl/holding_chamber_valve_insert.stl` (one plate) | PETG | The inhaler wedges into the body, the cap pushes into the body, the cap nozzle plugs into the mask. |
| 4 | `stl/holding_chamber_valve_flap.stl`, `stl/holding_chamber_umbrella.stl` (2 or 3 of each) | TPU | Flap and umbrella lie flat with no holes. Then assemble ([manual, section 5](MANUAL.md#5-assembly)). |

Measure your inhaler's mouthpiece before step 2. If it is not 25.4 x 19.6 mm, set `mouth_w`, `mouth_h` and `mouth_corner_r` in all three `.scad` files and regenerate. To skip the valves, print `stl/holding_chamber_one_piece_spacer.stl` in PETG instead of steps 3 and 4.

## Materials

| Material | Parts | Amount |
|---|---|---|
| TPU 95A | masks, inhalation flap, exhalation umbrella | about 15 g per mask, under 1 g per valve part |
| PETG (PLA works, but do not wash it hot) | chamber body, cap, valve insert, or the one-piece spacer | about 62 g for body + cap + insert |

Dry the TPU before printing the thin valve parts.

## Print settings

0.4 mm nozzle, 0.2 mm layers. Print every part as oriented in the STL, **without supports**.

| | TPU masks | TPU flap and umbrella | PETG chamber parts |
|---|---|---|---|
| Walls | 4 perimeters (5+ for the stem) | 3+ perimeters, 100 % infill | 5 perimeters, 4 top/bottom layers |
| Speed | 20 to 30 mm/s, first layer 15 | 15 to 20 mm/s | 40 to 60 mm/s |
| Nozzle / bed | 220 to 235 / 40 to 50 °C | 220 to 235 / 40 to 50 °C | 235 to 250 / 75 to 85 °C |
| Fan | 50 to 100 % | 100 % | 30 to 50 % |
| Brim | 3 mm if the stem lifts | 2 to 3 mm | 5 mm on the body |

Retraction short and slow for TPU. The full table and tips are in [manual section 3](MANUAL.md#3-printing).

## Customising

Open a file in `scad/` with OpenSCAD 2021.01 or newer, change parameters in the Customizer, press F6, export STL. To rebuild all STLs, renders, the paper template and the diagrams in one go:

```bash
python scripts/render.py
```

Run `python scripts/render.py stl` to rebuild only the STLs. The labelled diagrams also need `pip install -r scripts/requirements.txt`. See [manual section 9](MANUAL.md#9-customising-and-regenerating-the-stls).

## Repository layout

| Path | Contents |
|---|---|
| `scad/` | OpenSCAD sources: `cat_face_inhaler_mask.scad`, `round_cushion_inhaler_mask.scad`, `holding_chamber.scad` |
| `stl/` | ready-to-print parts with the default parameters |
| `docs/` | paper template and images used by the manual |
| `scripts/` | `render.py` (regenerates `stl/` and `docs/`), `diagrams.py` (labelled drawings) |
| `MANUAL.md` | printing and assembly manual |

## Credits

The two masks are parametric remakes of the static designs "maschera gatto ventolin v4" (cat face) and "inhalateur2" (round cushion), rebuilt from measurements of their meshes. Credit for the original shapes goes to their authors.
