# Creative silhouettes (`--design`)

Every module drafts a base block that follows common sewing practice. A **design** reshapes
that block on purpose: a five-point starfish sweatshirt, balloon legs, bell sleeves, a zigzag or
petal hem, a pointed elf hood, cat ears on a beanie, dinosaur spikes in a seam. Only use a design
when the user asks for a special shape; the defaults never change.

Own shapes only: when a user names a cartoon character ("Patrick Star", a brand mascot), build
an original shape that captures the idea (a chubby five-point star), never the character's face,
logo, colours as a costume or other protected artwork, and say so in one line.

## Workflow

1. **Turn the idea into features.** From a description, a sketch or an inspiration photo, pick a
   preset or write the feature list (JSON, below). Sketch/photo: read only the silhouette (where it
   is wider, narrower, pointed, longer); measurements still come from the user or the size table.
2. **Show the feature list and ask for confirmation** (exactly like photo mode A):
   ```bash
   python scripts/design.py describe starfish --garment hoodie
   python scripts/design.py describe my_design.json --garment pants_basic
   ```
   It lists every feature in words, the options the shape needs (e.g. no hem band under a pointed
   hem, no cuffs on a bell sleeve) and what is checked afterwards. Ask: "That's how I'd shape it:
   … Is that right?" Adjust on feedback.
3. **Generate** with the confirmed design:
   ```bash
   python scripts/generate.py --garment hoodie --size 128 --design starfish --options '{"title":"Starfish hoodie"}' --format a4
   python scripts/generate.py --garment skirt --size w38 --design my_design.json --format roll610
   ```
4. **Check and report.** `validation_report.md` gets three groups:
   - **Design (intended)**: every feature as an intended deviation from the base block (with the
     real offset range; "scaled to …%" when a seam was too short for the full shape);
   - **Freedom of movement**: girth along every reshaped zone after the design against the body
     plus a minimum ease (knits −5 %, wovens +4 %), and openings for head, hand, foot and hips.
     Tighter than body + minimum ease = ❌ (no print files);
   - **Design sewability**: tip angles of points (≥ 60° OK, < 35° ❌), inner corners (clip),
     steepness of a profile (≤ 1.0), appendages fit into their seam, can be turned (tip ≥ 40°,
     base ≥ 2.5 cm).
   Plus the normal checks on the reshaped pieces (seam lengths, angles, seam allowances, folds).
   Angles the design changes on purpose (pointed hem at the centre front) are marked "changed by
   the design (intended)". Look at the title-page views: they are drawn from the reshaped pieces.

## Presets

`python scripts/design.py presets`

| Preset | Shape | Garments |
|---|---|---|
| `starfish` | five-point star: round body, arms tapering to points, two pointed "legs" at the hem, pointed hood | hoodie, tshirt_basic, dress |
| `balloon` | rounded balloon body, narrow again at the hem | hoodie, tshirt_basic, dress |
| `bell_sleeves` | sleeves widening towards the hand (cuffs are switched off) | hoodie, tshirt_basic, dress |
| `zigzag_hem` / `petal_hem` | pointed zigzag / rounded scallop hem | tshirt_basic, hoodie, dress, skirt |
| `tulip_skirt` | rounded skirt with a curved hem | skirt, dress |
| `elf` | long pointed tip | hoodie (hood), beanie (crown) |
| `cat_ears` | two pointed ears on the crown | beanie |
| `dino_spikes` | a row of soft spikes in the hood or crown seam | hoodie, beanie |
| `balloon_legs` / `flared_legs` | wide rounded legs / legs widening to the hem | pants_basic |
| `wavy_loop` | wavy edges | loop |

Presets can be combined or changed: copy the features from `PRESETS` in `scripts/design.py`.

## Zones

`python scripts/design.py zones`. Every zone runs from **t = 0** (the attached end: underarm,
waist, crotch, neck) to **t = 1** (the free end: hem, wrist, front edge of the hood).

| Garment | Zones |
|---|---|
| tshirt_basic, hoodie, dress | `side`, `sleeve`, `hem`, `sleeve_hem`; hoodie also `hood` (centre seam); dress also `skirt_side` (the skirt hem is `hem`) |
| skirt | `side`, `hem` |
| pants_basic | `side`, `inseam`, `leg_hem` |
| beanie | `crown` (seam over the top), `sides`, `bottom` |
| loop | `long_edges` |

Aliases such as `sleeves`, `legs`, `body`, `cuff` are understood.

## Features (JSON)

```json
{"name": "Starfish", "inspiration": "chubby five-point star",
 "features": [
   {"zone": "side",   "bulge": {"at": 0.55, "cm": 3, "width": 0.9}},
   {"zone": "sleeve", "profile": [[0.3, 3], [0.85, 0.5]]},
   {"zone": "hem",    "shape": "points", "count": 2, "depth_cm": 7},
   {"zone": "hood",   "peak": {"at": 0.7, "cm": 9, "width": 0.5}},
   {"zone": "hood",   "appendage": {"shape": "spike", "count": 5, "height_cm": 4, "from": 0.2, "to": 0.9}}]}
```

Values are **cm per seam edge** (outwards +, inwards −); a side seam bulge of 3 cm adds 4 × 3 =
12 cm to the circumference of a top (front and back, left and right).

| Feature | Meaning |
|---|---|
| `profile: [[t, cm], …]` | offset at stations along the zone, smooth in between; missing ends are 0 |
| `bulge: {at, cm, width}` | one smooth rounding centred at `at` |
| `flare: {cm, from}` / `taper: {cm, from}` | wider / narrower towards the free end, starting at `from` |
| `peak: {at, cm, width, sharp}` | a point (hood tip, elf tip, ears on a crown seam) |
| `shape: points\|zigzag\|scallops\|waves\|curve`, `count`, `depth_cm`, `pieces` | hem or edge shape across the whole (unfolded) panel; `count` per panel (front, back, sleeve); `pieces: ["back"]` for a high-low hem |
| `appendage: {shape: spike\|ear\|round\|fin, count, height_cm, base_cm, from, to, stuffed, fabric}` | separate pieces sewn into the zone's seam (2 layers each, sewn, turned), with notches for their positions and their own booklet steps |

## Rules the engine keeps

- The same offset goes on both edges of a seam, measured from the free end, so the seam still
  matches. Ends sewn to something else (armhole, waistband, cuff, pocket) do not move and keep
  their angle; a free hem follows a moved corner.
- Shaped hems become narrow hems (allowance = the seam allowance, max. 1 cm, not turned up): finish
  with overlock/zigzag, turn 1 cm and topstitch, or use a facing; clip inner points.
- Shapes are kept in proportion: a profile steeper than 0.8 (short sleeve, doll clothes) and hem
  points deeper than 0.45 × their width are scaled down; the report says by how much.
- A design never makes a garment tighter than body + minimum ease without an ❌.
- Options the shape cannot have are switched off before drafting and listed in `describe`:
  hem band and kangaroo pocket under a shaped hem, cuffs under a bell sleeve or shaped sleeve hem,
  leg cuffs under a flared or shaped leg hem, the beanie brim under a shaped lower edge.

Not possible as a design (say so and offer an alternative): shapes that need new seams or darts
(a heart-shaped panel inserted into the front, a cape collar), stiff 3-D shapes that need
interfacing or wire, closures. Appendages can stand in for many 3-D ideas (spikes, ears, fins).
