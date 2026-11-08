# Changelog

All notable changes to this skill are listed here. Versions follow [semantic versioning](https://semver.org/).

## [Unreleased]

## [1.4.0] - 2026-11-08

### Changed
- **Leaner SKILL.md** (193 instead of 299 lines, about 40 % fewer tokens on every use): the workflow stays in SKILL.md; the option and format reference, machines, doll clothes and the photo mode B internals moved to `references/options.md`, `references/machines.md`, `references/doll_clothes.md` and `references/photo_guide.md`, loaded only when needed. SKILL.md no longer claims all output is English (`--lang de`).
- **Faster layouts and photo fits, same results**: the layout packer only searches the filled band of the page instead of the whole, mostly empty canvas (roll, A4, A0/A1, cutting layout about 2× faster); the DXF sheet uses the quick packing strategies; the top contour in the flat-lay model is computed for all positions at once (photo mode B for tops about 2× faster). Layouts and fitted values are identical.
- **CI in about 4 instead of 13 minutes**: tests run in parallel on all cores (`pytest-xdist`), the full suite with coverage runs once on Python 3.12, Python 3.10 runs the quick tests, and a new push to a PR cancels the older run.

## [1.3.0] - 2026-11-07

### Added
- **Automatic booklet check** (`scripts/booklet_qa.py`), run on every build: front/back views must show every band, cuff, sleeve and the hood and two separate legs for pants; stacked seam pieces must lie on each other; each picture must fill its area; no picture may fall back to the pictogram; no text may leave its panel or overlap another. Findings go into the "Booklet check" section of `validation_report.md`, into `run(...)["booklet_issues"]` and into the warnings; the tests require zero findings for the reference garments.
- **Contact sheets for the visual check** (`scripts/booklet_pages.py <pdf>`): every booklet page side by side with its page number; SKILL.md step 6 makes looking at every sheet mandatory before delivery.
- "Put one leg inside the other" is drawn like the reference: leg 1 wrong side out, leg 2 turned right side out and pushed in up to the top, the hidden part dotted. The last step is now "Final pressing" with an iron.
- README rewritten for prompting: example prompts, claude.ai zip install and update steps, and pictures for each feature (pattern, booklet, cutting layout, nested sizes, photo copy, doll clothes) in `docs/images/`; command line, options and tests moved to `docs/DEEP_DIVE.md`. New examples 5 (hoodie 140 with kangaroo pocket) and 6 (nested joggers 98/110/122); every example folder has its own README; `tools/make_examples.py images` rebuilds the README pictures and example READMEs.
- **Pants options** (#39): `fake_fly` (J topstitch line on the left front leg with its own step; the step only says the stitching catches the crotch seam allowance when it really does), `back_pockets: 1|2` with `back_pocket_side` (a single pocket is cut once and its mark names the leg), `hem_finish: "elastic_casing"` (hem allowance 5 mm + elastic + 10 mm, 3 cm opening at the inseam, elastic length per leg in the notes and steps), `pocket_bag_fabric` (the inner pocket bag becomes its own "Lining" group in the cutting layout and fabric consumption).
- **Overlocker without a sewing machine** (`--machines overlocker,hand` or `overlocker_only`): seams on the overlocker with 7.5 mm allowance (woven too), every straight-stitch step by hand (back stitch, blind stitch, tacking stitch, hand bar tack, a box of hand stitches for elastic), no separate edge-finishing steps, overlocker hints in the steps and the machines table, hem casing finished and folded once. (#39)
- **German output** (`--lang de`, spec `language`): every output text goes through one central string table (`scripts/i18n.py`, `scripts/i18n_de.py`), with German file names (`naehanleitung.pdf`, `pruefbericht.md`, `zuschnittplan.png`, `…_kleben.pdf` …), decimal commas and "Gr. 122". A test checks that the reference order leaves no English text in the Markdown, SVG and PDF outputs. (#39)
- **Booklet v2** (#39): title page with the finished garment from the front and the back and all key data (size, fabric amounts, notions, machines, seam allowance, parts/steps, difficulty and time); parts and material page with fabric colours (corduroy brown with wales, lining blue, rib green; right and wrong side differ) and a legend of colours and lines (red solid = machine, red dotted = by hand, blue dash-dot = fold line, chalk = marking) plus what "left/right (as worn)" means; basics pages for the machines in use (overlocker: allowance vs. knife and needle, test seam, curves, thread chain; hand stitches with a picture each; sewing machine); **two steps per page** with number badge, tool icons with labels, ×2 badge ("both legs"), picture left, 2–4 numbered actions right and yellow **Important** / green **Tip** boxes; ✓/✗ pictures for the single back pocket and for pressing a fabric with nap; a "Label the pieces" step with FL/FR/BL/BR tape tags for pants with a fake fly or one back pocket; magnifier insets with captions; 1:1 templates with a 5 × 5 cm control square (fake fly J line); a "Done!" page. Every text is wrapped to its measured width; a test checks that no text leaves its panel and no labels overlap, for pants, T-shirt, hoodie, skirt and dress.
- Option `title` for every garment: the name on the pieces, in the instructions and in the file names. (#39)
- Fabrics **corduroy** and **velvet**, with a nap: the cutting layout keeps every main-fabric piece waist up ("Nap ↓, all pieces waist up") and the fabric consumption follows; option `nap` for any other fabric. Pressing note per fabric (corduroy/velvet from the wrong side on a terry towel). (#39)

### Changed
- **Booklet layout after the reference booklet**: centred title page with size, fit and fabric in one line, large front and back views and a "Sewn with …" box with the machine and tool icons; the parts page shows every part large and at the same scale (big parts in the first row, bands and pockets below) with a navy count badge on the part, the seam allowances, the material in two columns (fabric amounts, notions, machines with their stitch settings, thread, clips, chalk, iron, towel) and "Colours in this booklet"; the basics page has a box per machine; steps get navy number badges and bullets, one-paragraph "⚠ Important:" / "Tip:" boxes and the ×2 badge bottom right; the "Done!" panel fills the free half of the last step page, the 1:1 templates come after it; page numbers at the bottom.
- Privacy: `project.json` from photo mode B stores only the photo's file name, not its full local path; `profiles/` and `*.smis` measurement exports are git-ignored so personal measurements don't get committed by accident.
- The back-pocket step uses the pattern's real seam allowance instead of a fixed 1 cm. (#39)

### Fixed
- **Front and back views** (title page, "Done!") are whole garments now (`scripts/views.py`): pants with both legs apart below the crotch, the centre seam, the waistband across the whole waist (gathered when it is elastic) and leg cuffs with the leg gathered into them; tops and dresses with both sleeves set into the armholes, cuffs, hem band, neckband or hood and the kangaroo pocket; the dress skirt gathered onto the bodice; skirts with their waistband. Before, harem pants showed a floating, too narrow back waistband and hoodies had no sleeves.
- **Seam pictures**: two pieces whose seam edges differ in shape (pants side seams and inseams, sleeve into armhole) are no longer stacked skewed across each other; they lie side by side, right side up, the seam edges facing each other and marked red, notches and "right sides together" between them. A side panel already sewn to the front is drawn on, so the side seam runs up to the waist. "Put one leg inside the other" shows the real legs; the kangaroo pocket is drawn whole on its placement (its mark was missing the corner at centre front).

## [1.2.0] - 2026-11-07

### Added
- **Illustrated sewing booklet**: `sewing_instructions.pdf` now starts with a vector booklet: cover with all parts, parts list with letters and counts, fabric and notions, machines and tools with the stitch settings, then numbered steps (six per page) with one action each. Every step has a picture drawn from the real pieces: the two pieces right sides together (right side shaded, wrong side hatched) with pins, stitch line, sewing direction and notches; bands closed into rings, folded, quartered and sewn on stretched; hems and topstitching with a cross-section detail; close-ups for short edges; ×2 for steps done on both legs/sleeves. Works for every garment, option and the doll mode. The reference pages (printing, measurements, pieces, validation) follow. (#37)
- Structured steps (`scripts/steps.py`): garment modules describe their construction with `assembly()`; the stitch kind of each step is turned into a machine and stitch (overlocker, coverstitch, sewing machine with zigzag/stretch stitch/twin needle) from the spec option `machines`. (#37)
- **Your machines** (`--machines sewing,overlocker,coverstitch,…`, spec `machines`, workshop file via
  `profiles.py machines set …`, or per profile): the skill asks which machines you sew with (sewing machine
  with zigzag or straight stitch only, stretch stitch, twin needle, overlocker, coverstitch) and adapts the
  pattern to them. Knit seams on the overlocker get 7.5 mm seam allowance, woven seams on a
  straight-stitch-only machine 15 mm for French seams; every seam and hem step names your machine and
  stitch, and the instructions get a "Your machines" table with stitch settings and needles per kind of
  step. `machines.method()` / `tool_for()` give the machine and stitch per step as data. (#36)
- Validation check for every cut-on-fold edge: straight, no seam allowance, neighbouring edges at 90° (no peak or dip at the centre once unfolded), on grain. (#35)
- The *Release* workflow can be started manually on `main` and creates the tag itself (#34)

### Changed
- **Cut-on-fold edges**: every fold edge now carries the standard bracket symbol (two arrows pointing at the fold, "PLACE ON FOLD") instead of a text-only label. It is sized to the edge, so short fold edges such as a doll waistband get "ON FOLD"/"FOLD" in a smaller font instead of text running off the piece, and it keeps clear of fold-over lines and the grainline; the label block no longer covers it. (#35)
- The sewing instructions explain how to cut the pieces marked "on fold" for the layout used (on the fabric fold, or opened out on a single layer), and the cutting layout marks opened-out fold pieces "(unfolded)". (#35)

## [1.1.0] - 2026-11-07

### Added
- **Doll clothes mode** (`generate.py --doll`): dress, skirt, pants and T-shirt for dolls, drafted from doll measurements with 6 mm seam allowance and a back opening with Velcro; also available in photo mode B (`--doll`) (#32).
- **Photo mode B for tops**: T-shirts and raglan tops from a flat-lay photo (`--type top`) (#30).
- **Nested multi-size patterns** (`--size 98,110,122`) with one PDF layer per size (#29).
- **Illustrated sewing instructions** with a diagram for every seam step (#28).
- **Fit adjustments** from test-garment feedback (#27).
- **Saved body-measurement profiles** per person (#26).
- **Dress module**: bodice + skirt, or A-line T-shirt dress (#25).
- **Hoodie zip-up jacket** variant (#24).
- **Pants options**: flared, bootcut and tapered legs, cargo pockets, shorts with turn-up (#23).
- **Imperial units** and US/UK size systems (#22).
- **Projector output**: single 1:1 page with calibration grid, light and dark (#21).
- **Configurable seam and hem allowance**, including patterns without allowance (#20).
- **Cutting layout on folded fabric** (double layer) (#19).
- **DXF (AAMA) export**, mirrored hem corners, notch projection, measurement files and construction values (#18).

### Changed
- README, SKILL.md, CONTRIBUTING and drafting rules aligned with the code (#31).

## [1.0.0] - 2026-11-06

First public version: pants, T-shirt, hoodie, skirt, beanie and loop modules; roll, A4, A0 and Letter output; validation report, sewing instructions, photo mode B for pants; CI, release workflow and contributor guide.
