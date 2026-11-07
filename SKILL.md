---
name: sewing-pattern-generator
description: Creates sewable, true-to-size, print-ready sewing patterns (1:1 vector PDF) from a free description, a size or body measurements and/or photos of a garment. Use for "make/draft/generate a sewing pattern", "pattern from my measurements", "pattern from a photo", "copy my favourite pants", "trace a garment", plotter/roll printing, A0/A1, or A4 pages to tape together. Also triggers on German requests such as "Schnittmuster erstellen/konstruieren", "Nähmuster nach Maßen", "Schnitt nach Foto/Vorbild", "Kleidungsstück abnehmen/nachnähen", "Lieblingshose kopieren", "A4 zum Kleben". Pants (joggers, harem pants, leggings, pull-on trousers), T-shirt/raglan, hoodie/sweatshirt/zip jacket, skirt, dress, beanie, loop scarf; doll clothes ("Puppenkleidung", "Kleider für die Stoffpuppe").
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
- **Machines:** which machines they sew with: sewing machine (zigzag? stretch stitch? or straight
  stitch only), twin needle, overlocker/serger, coverstitch. Skip the question when the workshop
  file already has them (`python scripts/profiles.py machines show`) or they named them before.
  Default if they don't say: a household sewing machine with zigzag.
- Seam allowance only if it matters to them (default 1 cm, hems 2–2.5 cm; with an overlocker on
  knits 7.5 mm automatically, 1.5 cm for woven on a straight-stitch-only machine, or "none" to
  trace and add their own)

Do not ask again afterwards; resolve anything unclear with a sensible default and say
so in the result.

**Doll clothes** (fabric doll, soft toy, fashion doll; height 20–100 cm): ask instead for the
doll's height (head to feet) and, measured with a tape or a string around the doll: chest,
waist, hip, head, arm length (shoulder to wrist), inseam and side length (waist to soles).
Only the height is required; missing values follow typical fabric-doll proportions. Then
`generate.py --doll --garment dress --measures '{"height": 45, "chest": 30, …}'`
(spec `"doll": true`). Supported: `dress`, `skirt`, `pants_basic`, `tshirt_basic`. Doll defaults
(each can be overridden): seam allowance 6 mm (5 mm under 30 cm), hems 10 mm, woven fabric, wide
fit, tops and dresses open completely at the back (Velcro/snaps, because a stuffed head rarely
fits through a neckline) with a bias-bound neckline, pants with a narrow elastic casing, no
pockets/cuffs. Recommend thin cotton, a short stitch and fray stop. A doll gets a profile with
`profiles.py save rosa --measures '{…}' --kind doll`. Details: `scripts/doll.py`,
`references/size_tables.md` ("Doll clothes").

**Machines:** pass them with `--machines sewing,overlocker,coverstitch` (keys: `sewing` = straight
stitch + zigzag, `straight_only`, `stretch_stitch`, `twin_needle`, `overlocker`, `coverstitch`;
German names such as Overlock, Coverlock, Zwillingsnadel work too; spec field `machines`). The
machines belong to the person who sews, so the first time they name them, save them once for all
future patterns: `python scripts/profiles.py machines set sewing,overlocker` (workshop file
`profiles/_machines.json`; a measurement profile may carry its own `--machines`, and `--machines`
wins over both). Effects: knit seams on the overlocker get 7.5 mm allowance (the knife trims),
woven seams on a straight-stitch-only machine 15 mm for French seams (an explicit
`--seam-allowance` always wins; doll clothes keep their 6 mm); every seam and hem step names the
machine and stitch; the instructions get a "Your machines" table (stitch, width/length, needle per
kind of step) and tips for what is missing (e.g. a twin needle instead of a coverstitch). Without
an overlocker nothing is missing: knit seams use a narrow zigzag/stretch stitch. A knit on a
straight-stitch-only machine works but is fragile: suggest a woven fabric or the double row of
long straight stitches the instructions describe. **No sewing machine at all** (only an
overlocker): `--machines overlocker,hand` (or `overlocker_only`; `hand` without any sewing-machine
key means "no sewing machine"). Then every seam is overlocked (7.5 mm allowance, woven fabric too)
and every straight-stitch step is done by hand: topstitching → back stitch, hems/casings → blind
stitch, basting → tacking stitch, bar tacks by hand, elastic ends → a box of hand stitches; the
steps add overlocker hints (pins out before the knife, curves slowly, thread chains). In the reply,
mention in one line how the pattern was adapted to their machines.

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
Doll clothes can be copied too: add `--doll` (`reverse.pipeline.run(..., doll=True)`); the
result has doll allowances and a back opening, and `generate.py --project` prints it. Doll tops
measure best with long sleeves (very short, wide doll sleeves: take the sleeve width with a tape).
Mode B works for **pants** (`--type pants`) and for **T-shirts / raglan tops**
(`--type top`, module `tshirt_basic`). For tops the photo gives chest and hem width, length,
underarm depth, the front neckline (width and depth), back neck depth, the shoulder point,
the sleeve top line, upper-arm width, sleeve reach and opening; set-in or raglan is detected
from the neckline (a raglan seam leaves it at a sharp corner) and shown in the overlay for
the user to confirm (`base_options={"sleeve_style": "raglan"}` overrides it). The fit drafts
candidate patterns, lays them out flat virtually (`flatlay.py`: front ∪ back, sleeve folded
along its top line) and matches every photo feature by least squares. The scale comes from
the 10 cm card; for a garment 1.5 m wide (long sleeves spread out) a slight camera tilt can
shift it by up to 2 %: if the user can, have them measure the chest width flat with a tape
and pass it as `tape={"chest_flat": 37.2}` (cm): every photo value is then rescaled to it.

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
**Several sizes at once (nested):** `--size 98,110,122` (or a range `98-122` in kids' steps)
drafts and validates every size and overlays them at a shared construction point, each size in
its own colour/line, PDF layer (switch sizes on/off in Acrobat's *Layers* panel) and SVG group.
Use it for siblings or to blend between sizes; all sizes share the same options.
Imperial users: `--units imperial` (measurements in inches, reports in inches/yards).

**German output:** `--lang de` (spec `"language": "de"`) writes every output in German: piece labels, sewing
steps, booklet, cutting layout, reports and diagrams, with German file names (`naehanleitung.pdf`,
`pruefbericht.md`, `zuschnittplan.png`, `schnitt.json`, `…_master_1zu1.svg`, `…_a4_kleben.pdf`), decimal
commas and "Gr. 122". All texts go through one string table (`scripts/i18n.py`, German entries in
`scripts/i18n_de.py`); a new output text needs a German entry there. Option names and construction value keys stay English.

Modules and main options:

| Module | Styles/options |
|---|---|
| `pants_basic` | style: jogger, harem, leggings, trousers · fit · fabric · stretch · length (long, 7/8, knee, short) · waistband (casing, rib, yoga, tunnel) · cuffs · pockets ([side] = slanted front pocket with pocket bag, [back_patch], [cargo]) · leg_shape (straight, tapered, bootcut, flare + flare_cm; long legs without cuffs) · turn_up (cm, shorts/knee length) · fake_fly (true or {offset_mm, length_frac_R, radius_mm, side}) · back_pockets (1, 2) + back_pocket_side (right, left; as worn) · hem_finish (plain, elastic_casing + hem_elastic_mm, hem_elastic_len_cm) · pocket_bag_fabric (cotton, jersey, lining, main) |
| `tshirt_basic` | fit · fabric · sleeve_style (set_in, raglan) · sleeve_length (short, 3/4, long) · neckline (round, v) · length (normal, tunic) · sleeve_cuffs · hem_band |
| `hoodie` | like the T-shirt + hood, hood_lining, kangaroo (default: sweat, wide, rib cuffs) · front (closed, zip: zip-up jacket with split front, side pockets, zip guard, zip length in the notes) · zip_guard |
| `skirt` | style: gathered, a_line, circle · length (mini, knee, midi, maxi) · gather · flare_deg |
| `dress` | style: waist_seam (T-shirt bodice + skirt: gathered, a_line, circle; gather 1.0–2.5; waist_elastic; pockets in the side seam), shirt_dress (A-line T-shirt dress, flare_cm) · length (mini, knee, midi, maxi) · all T-shirt sleeve/neckline options |
| `beanie` | brim, slouch |
| `loop` | wraps (1 = single, 2 = worn doubled), height |

Fabrics: woven, corduroy, velvet, jersey, jersey_elastane, interlock, sweat, fleece, rib. Corduroy and
velvet have a nap (option `nap`, also `nap: true` for any other fabric): every main-fabric piece is
cut with the top towards the same fabric end, and the pressing note says to press from the wrong side.
All modules: `title` (e.g. "Kordhose") replaces the garment name on the pieces, in the instructions and
in the file names.
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
instructions (PDF: IKEA-style booklet with cover, parts list, machines and tools, then one action per
step, each drawn from the real pieces; plus Markdown with a PNG per step in `steps/`), `pattern.json`,
`validation_report.md`. The steps follow the machines the user owns (spec option `machines`, e.g.
`["sewing", "overlocker", "coverstitch"]`): overlocker seams, coverstitch hems, otherwise zigzag/twin needle.
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

**Toile feedback:** after delivery, offer once: "Tell me how the test garment fits (e.g. 'hip
2 cm too tight, crotch 1.5 cm too low') and I'll adjust the pattern." Then
`--adjust '{"hip_tight": "2cm", "crotch_low": "1.5cm"}'` (or signed changes such as
`{"hip": "+2cm", "sleeve_length": "-3cm"}`; spec field `adjustments`). The instructions show
before/after finished measurements; the adjustments stay in `pattern.json`/`project.json`
and are re-applied in other sizes. Keys: `references/drafting_rules.md` §8.

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
- Not covered (offer the alternative): dresses with closures/darts (woven fitted bodices),
  lined/woven jackets, shirts/blouses with collar and button placket, jeans with a fly,
  welt/jetted pockets, style lines, overalls, bodysuits.
- Grading uses grading rules per size step (`reverse/store.py`), never linear scaling.

## Files
- `scripts/generate.py`: complete flow (CLI)
- `scripts/i18n.py`, `i18n_de.py`: output language (`--lang de`), one central string table
- `scripts/geometry.py`, `pattern.py`, `measurements.py`, `ease.py`, `units.py`, `allowance.py`:
  foundations (geometry, pieces, sizes, ease, imperial units, seam allowances)
- `scripts/construction.py`, `adjust.py`, `notches.py`: construction values, toile adjustments, notches
- `scripts/profiles.py`, `measure_files.py`: measurement profiles, the machines workshop file and
  `.smis`/`.vit` files
- `scripts/machines.py`: the sewist's machines → seam allowances, seam/hem methods, "Your machines"
  table (`method(options, kind, knit)` / `tool_for` per step kind: seam, finish, hem, topstitch, band)
- `scripts/nested.py`, `export_dxf.py`: nested multi-size patterns, DXF export
- `scripts/garments/*.py`: garment modules `draft(measures, options) -> Pattern`
- `scripts/doll.py`: doll clothes mode (doll measurements, virtual drafting scale, doll defaults)
- `scripts/validate.py`: sewability checks
- `scripts/layout.py`, `render.py`, `instructions.py`: layout, PDF/SVG/PNG, instructions
- `scripts/steps.py`, `diagrams.py`, `booklet.py`: one-action sewing steps (garment `assembly()`), the
  machine/stitch choice per step, step diagrams from the real pieces, the IKEA-style booklet PDF
- `scripts/photo_analyze.py`, `photo_measure.py`, `flatlay.py`, `reverse/`: photo modes A and B
- `scripts/refcard.py`: writes `assets/reference-card.pdf`; `photo_synth.py`: test photos
- `references/`: drafting rules, size tables, print specs, photo guide
- `tests/`: `python -m pytest tests`
