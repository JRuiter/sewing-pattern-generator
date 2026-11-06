---
name: sewing-pattern-generator
description: Creates sewable, true-to-size, print-ready sewing patterns (1:1 vector PDF) from a free description, a size or body measurements and/or photos of a garment. Use for "make/draft/generate a sewing pattern", "pattern from my measurements", "pattern from a photo", "copy my favourite pants", "trace a garment", plotter/roll printing, A0/A1, or A4 pages to tape together. Also triggers on German requests such as "Schnittmuster erstellen/konstruieren", "Nähmuster nach Maßen", "Schnitt nach Foto/Vorbild", "Kleidungsstück abnehmen/nachnähen", "Lieblingshose kopieren", "A4 zum Kleben". Pants (joggers, harem pants, leggings, pull-on trousers), T-shirt/raglan, hoodie/sweatshirt/zip jacket, skirt, dress, beanie, loop scarf.
---

# Sewing pattern generator

Drafts sewing patterns **parametrically** (drafting rules, no image generation), checks
that they can be sewn, and produces print files, a cutting layout, fabric consumption
and sewing instructions. All generated files are in English. Reply to the user in the
language they write in.

Own constructions only: never rebuild or copy protected commercial patterns. When the
user shows a designer garment, draft an original pattern in a similar style for private
use.

## Setup (once)

```bash
pip install -r requirements.txt   # numpy scipy shapely opencv-contrib-python-headless reportlab matplotlib pillow pypdf
```

All scripts live in `scripts/` and are called from there or with their path.

## Workflow

### 1. Understand the request
Pick out: garment and variants, size or measurements, fabric and stretch, fit, output
format. Photos? → step 3.

### 2. Questions: exactly ONE round, only what is really missing
Ask for the missing points together in one short message, each with a default
("If you don't say otherwise, I'll use …"). Typical gaps:
- Garment and variants (pockets, cuffs, length, hood …)
- Size (kids 86–176, women 34–56, men 44–60) **or** body measurements
  (height, chest, waist, hip, inseam, side length, arm length, head)
- Fabric (woven / jersey / jersey with elastane / interlock / sweat / fleece) and stretch in %
- Fit (slim / normal / wide / oversized; for pants also harem)
- Output: roll (width in mm, default 610), A0, A1, A4 or US Letter to tape together
- Seam allowance only if it matters to them (default 1 cm, hems 2–2.5 cm; e.g. 0.75 cm for
  the overlocker, 1.5 cm for woven, or "none" to trace and add their own)

Do not ask again afterwards; resolve anything unclear with a sensible default and say
so in the result.

**Measurement profiles:** when the user gives body measurements for a person, offer once to
save them (`python scripts/profiles.py save lena --measures '{…}' --kind child`). Later
requests such as "trousers for Lena" then need no measurement questions:
`generate.py --profile lena …` (warns if a child's measurements are older than 6 months;
see `references/size_tables.md`).

### 3. Photos (optional)
First decide which mode applies (details: `references/photo_guide.md`):

**Mode A: inspiration photo** (worn, catalogue, Pinterest). Look at the photo and fill in
the feature JSON (schema in `scripts/photo_analyze.py`, each feature with `value` and
`confidence` 0–1). Then:
```bash
python scripts/photo_analyze.py features.json        # confirmation text + module/options + "not covered"
python scripts/photo_analyze.py --image flatlay.jpg  # pants silhouette automatically (proportions only)
```
Show the feature list with confidences and ask the user to confirm ("I can see … is that
right?"). Name features that are not covered openly and offer the alternative the script
prints; do not improvise. **Body measurements always come from the user**, never from an
inspiration photo.

**Mode B: copy a garment** (laid flat, photographed straight from above, with the
reference card `assets/reference-card.pdf` or a folding ruler): reverse engineering.
```bash
cd scripts && python -m reverse.pipeline photo.jpg --type pants --out project/
```
Results: `overlay_measurement.png` (detected outline and measurements; show it to the
user to confirm), `reverse_report.md` (piece/seam graph, target/actual/Δ deviation
report, sewability check) and `project.json` (keep it for "like last time, 2 sizes
bigger" → `reverse.pipeline.regrade("project.json", 2)`). Tape-measure values from the
user take precedence: `photo_measure.measure(..., tape={"inseam": 48})`. If the card is
missing, the skill says exactly what to do. Missing photos (e.g. for the crotch curve)
are listed by `reverse.decompose.missing_photos`. Tolerance: lengths ± 1 cm, widths ± 2 %.
Then the print files:
```bash
python scripts/generate.py --project project/project.json --format roll610,a4 --out out/copy
```
Mode B is fully automated for **pants**; tops are measured roughly (`--type top`: chest
width, hem width, length, sleeve) and fitted with `tshirt_basic.fit_to_targets`. Ask for
armhole and neckline measurements with a tape measure in that case.

### 4. Measurements
`measurements.complete_measures(given_cm, size)` fills in missing measurements from the
size table or body height and reports plausibility warnings. Given measurements take
precedence over the table. Tables and sources: `references/size_tables.md`.
If the user has an XML measurement file from pattern CAD software (`.smis` / `.vit`),
pass it with `--measures-file`; explicit `--measures` values override it. With
`--export-measures` the measurements used are saved as `body_measurements.smis`, a good
way to keep a person's measurements for next time.

### 5. Draft, validate, lay out, render: one call
```bash
python scripts/generate.py --garment pants_basic --style harem --size 122 \
    --fabric sweat --format roll610,a4 --out out/harem122
# more examples
python scripts/generate.py --garment tshirt_basic --size 140 --options '{"sleeve_style":"raglan","sleeve_length":"long"}' --format a4
python scripts/generate.py --garment hoodie --size w38 --fabric sweat --format roll914,a0
python scripts/generate.py --garment skirt --size 128 --style circle --format a1
python scripts/generate.py --spec order.json          # everything as JSON (see the header of generate.py)
```
Sizes: kids as a number (`122`), women as `w38`, men as `m52`; US/UK: `us8` (US women's),
`uk12` (UK women's), `us3t` (US toddler), `usk8` (US kids), see `references/size_tables.md`.
Imperial users: `--units imperial` (measurements in inches, reports in inches/yards).

Modules and main options:

| Module | Styles/options |
|---|---|
| `pants_basic` | style: jogger, harem, leggings, trousers · fit · fabric · stretch · length (long, 7/8, knee, short) · waistband (casing, rib, yoga, tunnel) · cuffs · pockets ([side], [slant], [back_patch], [cargo]) · leg_shape (straight, tapered, bootcut, flare + flare_cm; long legs without cuffs) · turn_up (cm, shorts/knee length) |
| `tshirt_basic` | fit · fabric · sleeve_style (set_in, raglan) · sleeve_length (short, 3/4, long) · neckline (round, v) · length (normal, tunic) · sleeve_cuffs · hem_band |
| `hoodie` | like the T-shirt + hood, hood_lining, kangaroo (default: sweat, wide, rib cuffs) · front (closed, zip: zip-up jacket with split front, side pockets, zip guard, zip length in the notes) · zip_guard |
| `skirt` | style: gathered, a_line, circle · length (mini, knee, midi, maxi) · gather · flare_deg |
| `dress` | style: waist_seam (T-shirt bodice + skirt: gathered, a_line, circle; gather 1.0–2.5; waist_elastic; pockets in the side seam), shirt_dress (A-line T-shirt dress, flare_cm) · length (mini, knee, midi, maxi) · all T-shirt sleeve/neckline options |
| `beanie` | brim, slouch |
| `loop` | wraps (1 = single, 2 = worn doubled), height |

Fabrics: woven, jersey, jersey_elastane, interlock, sweat, fleece, rib.
Fits: slim, normal, wide, oversized, harem.

Seam allowance (all modules): `--seam-allowance 7.5` (mm, all seams), `--hem-allowance 30`
(turned-up hems), `--seam-allowance none` (pattern without allowances: only the seam line is
drawn and every piece lists what to add). Spec options: `seam_allowance_mm`,
`hem_allowance_mm`, `seam_allowance: "none"`. Fold edges stay at 0; casings, facings and the
narrow circle-skirt hem keep their construction allowance.

Formats: `rollNNN` (page width = roll − 10 mm, portrait; pieces wider than the roll are
split automatically into strips with glue marks), `a0`, `a1` (pieces whole, oversized
pieces tiled), `a4`, `letter` (tiles with 10 mm overlap and an overview page), `dxf` /
`dxf14` (DXF for cutting machines and CAD, AAMA layers, see `references/print_specs.md`),
`projector` / `projector_dark` (one page 1:1 for projector sewing, 10 cm calibration grid,
thick lines).
Always written as well: SVG master 1:1, PNG preview, cutting layout PNG, sewing
instructions (MD + PDF), `pattern.json`, `validation_report.md`.
Cutting layout: `--fabric-layout auto|folded|single` (default `auto` = the shorter of
folded selvage to selvage and single layer; see `references/print_specs.md`).

**Validation is mandatory:** if a check fails (❌), `generate.py` exits with code 2 and
writes **no** print files. Fix the cause from `validation_report.md` (usually
contradictory measurements/options) and generate again. Never deliver a pattern with
errors. Rules: `references/drafting_rules.md`.

Fine tuning: the report lists the **construction values** (hip width, crotch extensions,
rise, armhole depth, …) with how they were derived. To change one, e.g. after a toile
("seat too tight" → larger `back_crotch_extension`), pass
`--construction '{"back_crotch_extension": 95}'` (mm) and generate again; validation
still checks the result. Notch shape: `--notch-style slit|t|v` (v for cutting machines and
projector use).

### 6. Check the preview yourself
**Look at** the PNG preview(s) and the cutting layout before delivering: all pieces
present, nothing overlapping, labels readable, grainline plausible, control square
present. Fix anything odd or tell the user openly.

### 7. Deliver to the user
- PDFs (roll/sheets/A4), SVG master, preview PNG
- Sewing instructions with fabric consumption and cutting layout
- **Validation table** (content of `validation_report.md`) in the reply
- Printing note: "Print at **100 % / Actual size**, not 'Fit to page'. Measure the control
  square (5 × 5 cm)." For the Canon iPF650 (24" roll): set the PDF as a custom size
  600 mm × length, portrait, via Direct Print & Share or Acrobat
  (`references/print_specs.md`).
- **Test garment note:** "The first time you sew a new pattern, please make a test
  garment from inexpensive fabric with similar stretch and check the fit."

## Limits (say so openly)
- **Exact measurements cannot be derived** from photos of worn garments, only style and
  proportions. Exact measurements only with mode B (scale in the picture) or a tape
  measure.
- The back and hidden details are asked about, never invented.
- Not covered (offer the alternative): dresses with closures/darts (woven fitted bodices), lined/woven jackets, shirts/blouses
  with collar and button placket, jeans with a fly, cargo/welt pockets, style lines,
  flared legs.
- Grading uses grading rules per size step (`reverse/store.py`), never linear scaling.

## Files
- `scripts/generate.py`: complete flow (CLI)
- `scripts/geometry.py`, `pattern.py`, `measurements.py`, `ease.py`: foundations
- `scripts/garments/*.py`: garment modules `draft(measures, options) -> Pattern`
- `scripts/validate.py`: sewability checks
- `scripts/layout.py`, `render.py`, `instructions.py`: layout, PDF/SVG/PNG, instructions
- `scripts/photo_analyze.py`, `photo_measure.py`, `reverse/`: photo modes A and B
- `scripts/refcard.py`: writes `assets/reference-card.pdf`; `photo_synth.py`: test photos
- `references/`: drafting rules, size tables, print specs, photo guide
- `tests/`: `python -m pytest tests`
