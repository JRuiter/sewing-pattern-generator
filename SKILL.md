---
name: sewing-pattern-generator
description: Creates sewable, true-to-size, print-ready sewing patterns (1:1 vector PDF) from a free description, a size or body measurements and/or photos of a garment. Use for "make/draft/generate a sewing pattern", "pattern from my measurements", "pattern from a photo", "copy my favourite pants", "trace a garment", plotter/roll printing, A0/A1, or A4 pages to tape together. Also triggers on German requests such as "Schnittmuster erstellen/konstruieren", "Nähmuster nach Maßen", "Schnitt nach Foto/Vorbild", "Kleidungsstück abnehmen/nachnähen", "Lieblingshose kopieren", "A4 zum Kleben". Pants (joggers, harem pants, leggings, pull-on trousers), T-shirt/raglan, hoodie/sweatshirt/zip jacket, skirt, dress, beanie, loop scarf; doll clothes ("Puppenkleidung", "Kleider für die Stoffpuppe").
---

# Sewing pattern generator

Drafts sewing patterns **parametrically** (drafting rules, no image generation), checks
that they can be sewn, and produces print files, a cutting layout, fabric consumption
and sewing instructions. Generated files are in English, or in German with `--lang de`.
Reply to the user in the language they write in.

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

**Doll clothes** (fabric doll, soft toy, fashion doll; height 20–100 cm): ask for the doll's
height and the doll measurements instead; only the height is required. Then `generate.py --doll …`.
Questions, defaults and the doll profile: `references/doll_clothes.md`.

**Machines:** pass them with `--machines sewing,overlocker,coverstitch` and, the first time the
user names them, save them for all future patterns (`python scripts/profiles.py machines set …`).
They change seam allowances and every seam/hem step (overlocker only: `--machines overlocker,hand`).
Keys, effects and the "no sewing machine" case: `references/machines.md`. In the reply, mention in
one line how the pattern was adapted to their machines.

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
Doll clothes can be copied too (`--doll`, see `references/doll_clothes.md`). Mode B works for
**pants** (`--type pants`) and **T-shirts / raglan tops** (`--type top`); set-in vs. raglan detection,
the flat-lay fit and the `tape={"chest_flat": …}` scale fix: `references/photo_guide.md`
("For Claude: mode B details").

### 3b. Creative shapes (optional, only when asked)
Special silhouettes ("a sweatshirt shaped like a starfish", balloon legs, bell sleeves, zigzag hem,
elf hood, cat ears, dino spikes) go on top of the normal base block as explicit design features,
for every module. Turn the description, sketch or photo into a preset or feature list, show it
with `python scripts/design.py describe <preset|design.json> --garment <module>` and let the user
confirm it, then generate with `--design`. The report lists every feature as an intended deviation
and re-checks room to move and sewability. Characters/brands: an own shape only, never their
artwork. Presets, zones, feature JSON and rules: `references/creative_designs.md`.

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
Sizes: kids `122`, women `w38`, men `m52`, US/UK `us8`/`uk12`/`us3t`/`usk8`; several sizes nested
with `--size 98,110,122`; `--units imperial`; **German output** `--lang de`. Modules: `pants_basic`,
`tshirt_basic`, `hoodie`, `skirt`, `dress`, `beanie`, `loop`. Formats: `rollNNN`, `a0`, `a1`, `a4`,
`letter`, `dxf`, `projector`. Seam allowance `--seam-allowance 7.5|none`, `--hem-allowance 30`.
**Look up every module option, fabric, format and output file in `references/options.md`** before
promising a variant; do not guess option names.

Always written as well: SVG master 1:1, PNG preview, cutting layout PNG, the illustrated sewing
booklet (PDF and Markdown with a PNG per step), `pattern.json` and `validation_report.md`.

**Validation is mandatory:** if a check fails (❌), `generate.py` exits with code 2 and
writes **no** print files. Fix the cause from `validation_report.md` (usually
contradictory measurements/options) and generate again. Never deliver a pattern with
errors. Rules: `references/drafting_rules.md`.

Fine tuning: the report lists the **construction values** with how they were derived; override
one with `--construction '{"back_crotch_extension": 95}'` (mm). **Toile feedback:** after delivery,
offer once: "Tell me how the test garment fits (e.g. 'hip 2 cm too tight') and I'll adjust the
pattern", then `--adjust '{"hip_tight": "2cm"}'`. Details: `references/options.md`.

### 6. Check the preview and the booklet yourself (never skip)
**Look at** the PNG preview(s) and the cutting layout before delivering: all pieces
present, nothing overlapping, labels readable, grainline plausible, control square
present.

**The booklet has two safety nets; both must pass before you deliver:**
1. **Automatic check** (`booklet_qa.py`, runs on every build): `validation_report.md` ends with
   "Booklet check" and `generate.run()` returns `booklet_issues`. It finds garment views without
   their bands, cuffs, sleeves or hood or with joined legs, stacked seam pictures whose edges do
   not lie on each other, almost empty pictures, the fallback pictogram, and text outside its
   panel or overlapping. Any finding = fix the drawing code (or say so openly), never deliver silently.
2. **Visual check:** `python scripts/booklet_pages.py <out>/sewing_instructions.pdf` writes contact
   sheets (4 pages each) to `<out>/booklet_check/`. **Open and look at every sheet** and check:
   - title page: the finished garment looks like the garment (two legs, waistband across the
     waist, cuffs at the hems; sleeves, hood, pocket where they belong), front and back at one scale;
   - every seam picture: the pieces are either exactly on top of each other along the seam or
     side by side with the two seam edges facing each other (red), never skewed across each other;
   - every picture shows what its text says (e.g. "one leg inside the other" shows legs, not boxes),
     fills its area and has no labels on top of lines;
   - nothing cut off, no empty half pages except the end.
   If something looks odd, fix it in `views.py`/`diagrams.py`/`booklet.py`, rebuild and look again.
   Delete `booklet_check/` before delivering (it is only for you).

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
- `scripts/generate.py`: complete flow (CLI); `scripts/garments/*.py`: garment modules
- `scripts/validate.py`, `booklet_qa.py`, `booklet_pages.py`: sewability checks, booklet checks, contact sheets
- `scripts/photo_analyze.py`, `photo_measure.py`, `reverse/`: photo modes A and B
- `scripts/profiles.py`: measurement profiles and the machines workshop file
- `scripts/design.py`: creative silhouettes (presets, zones, feature list, re-checks)
- `references/`: `options.md` (all options and formats), `machines.md`, `doll_clothes.md`, `creative_designs.md`,
  `drafting_rules.md`, `size_tables.md`, `print_specs.md`, `photo_guide.md`
- Developer docs (module layout, adding a garment): `CONTRIBUTING.md` in the repository
