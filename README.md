# areocat

3D-printable, parametric (OpenSCAD) adapters for giving a cat a metered-dose inhaler (Ventolin / salbutamol type pMDI):

- **two TPU face masks** that push straight onto the inhaler mouthpiece: an anatomical *cat face* mask with a tilted rim, and a *round* mask with a soft hollow rolled lip;
- **a small valved holding chamber** (about 105 ml) that goes between the inhaler and either mask, with a TPU flap inhalation valve and a TPU umbrella exhalation valve. A valveless one-piece spacer is included as a simpler alternative.

The masks come ready to print for cats of **3.3, 4, 5 and 6 kg**; the chamber is the same for every size. All parts fit a **25.4 x 19.6 mm** inhaler mouthpiece. Size and mouthpiece are parameters.

![All parts in print orientation: TPU amber, PETG blue](docs/img/print_layout.png)

> **Hobby designs, not medical devices.** Use them only with your veterinarian's guidance and dosing instructions, check every part for sharp edges before it touches your cat, and never force a mask on a struggling animal. The printed valves have not been laboratory tested.

**[Read the full manual](MANUAL.md)**: measuring, sizing, detailed print settings, assembly, fitting the mask, cleaning and troubleshooting.

## Sizes

![Cat face (back) and round (front) masks for 3.3, 4, 5 and 6 kg cats](docs/img/mask_sizes.png)

Each `stl/<weight>kg/` folder has both masks and a 1:1 paper template of the cat face mask rim for that size. `stl/common/` has the chamber parts, which fit every mask: the inhaler socket is the same in all sizes.

| Cat weight | Folder | Cat face mask rim | Cat face mask height | Round mask diameter | Round mask height |
|---|---|---|---|---|---|
| 3.3 kg | [`stl/3.3kg/`](stl/3.3kg/) | 42.7 x 44.3 mm | 48.8 mm | 39.7 mm | 35.8 mm |
| 4 kg | [`stl/4kg/`](stl/4kg/) | 45.5 x 47.2 mm | 50.6 mm | 42.3 mm | 36.9 mm |
| 5 kg | [`stl/5kg/`](stl/5kg/) | 49.1 x 50.9 mm | 52.8 mm | 45.6 mm | 38.3 mm |
| 6 kg | [`stl/6kg/`](stl/6kg/) | 52.1 x 54.1 mm | 54.7 mm | 48.4 mm | 39.4 mm |

Weight is only a starting point: an overweight cat does not have a bigger face. Print the templates of the two nearest sizes and pick the one that covers nose and mouth while staying below the eyes. For another size, set `cat_weight_kg` (or the rim size in mm) in the mask file.

## Print order

Print and test in this order, so a wrong size shows up before you have printed everything. `<size>` is your folder, for example `4kg`.

| # | Print | Material | Check before moving on |
|---|---|---|---|
| 1 | `stl/<size>/cat_face_rim_template_<size>.svg` on paper at 100 % | paper | The 50 mm bar measures 50 mm; the outline covers nose and mouth and stays below the eyes. Otherwise try the next size. |
| 2 | `stl/<size>/cat_face_inhaler_mask_<size>.stl` or `stl/<size>/round_cushion_inhaler_mask_<size>.stl` | TPU | The inhaler wedges firmly into the socket. Mask plus inhaler already works without a chamber. |
| 3 | `stl/common/holding_chamber_body.stl`, `holding_chamber_cap.stl`, `holding_chamber_valve_insert.stl` (one plate) | PETG | The inhaler wedges into the body, the cap pushes into the body, the cap nozzle plugs into the mask. |
| 4 | `stl/common/holding_chamber_valve_flap.stl`, `holding_chamber_umbrella.stl` (2 or 3 of each) | TPU | Flap and umbrella lie flat with no holes. Then assemble ([manual, section 5](MANUAL.md#5-assembly)). |

Measure your inhaler's mouthpiece before step 2. If it is not 25.4 x 19.6 mm, set `mouth_w`, `mouth_h` and `mouth_corner_r` in all three `.scad` files and regenerate. To skip the valves, print `stl/common/holding_chamber_one_piece_spacer.stl` in PETG instead of steps 3 and 4.

## Materials

| Material | Parts | Amount |
|---|---|---|
| TPU 95A | masks, inhalation flap, exhalation umbrella | 15 to 19 g per mask (3.3 to 6 kg), under 1 g per valve part |
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

Open a file in `scad/` with OpenSCAD 2021.01 or newer, change parameters in the Customizer, press F6, export STL. To rebuild all STLs and paper templates for every size, plus the renders and diagrams, in one go:

```bash
python scripts/render.py
```

Run `python scripts/render.py stl` to rebuild only the STLs. The exported cat weights are the `SIZES` list at the top of `scripts/render.py`. The labelled diagrams also need `pip install -r scripts/requirements.txt`. See [manual section 9](MANUAL.md#9-customising-and-regenerating-the-stls).

## Repository layout

| Path | Contents |
|---|---|
| `scad/` | OpenSCAD sources: `cat_face_inhaler_mask.scad`, `round_cushion_inhaler_mask.scad`, `holding_chamber.scad` |
| `stl/<weight>kg/` | both masks and the rim paper template for one cat size |
| `stl/common/` | holding chamber parts and the one-piece spacer, for every size |
| `docs/img/` | images used by the README and the manual |
| `scripts/` | `render.py` (regenerates `stl/` and `docs/`), `diagrams.py` (labelled drawings) |
| `MANUAL.md` | printing and assembly manual |

## Credits

The two masks are parametric remakes of the static designs "maschera gatto ventolin v4" (cat face) and "inhalateur2" (round cushion), rebuilt from measurements of their meshes. Credit for the original shapes goes to their authors.
