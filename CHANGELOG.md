# Changelog

All notable changes to this skill are listed here. Versions follow [semantic versioning](https://semver.org/).

## [Unreleased]

### Added
- **IKEA-style sewing booklet**: `sewing_instructions.pdf` now starts with a vector booklet: cover with all parts, parts list with letters and counts, fabric and notions, machines and tools with the stitch settings, then numbered steps (six per page) with one action each. Every step has a picture drawn from the real pieces: the two pieces right sides together (right side shaded, wrong side hatched) with pins, stitch line, sewing direction and notches; bands closed into rings, folded, quartered and sewn on stretched; hems and topstitching with a cross-section detail; close-ups for short edges; ×2 for steps done on both legs/sleeves. Works for every garment, option and the doll mode. The reference pages (printing, measurements, pieces, validation) follow.
- Structured steps (`scripts/steps.py`): garment modules describe their construction with `assembly()`; the stitch kind of each step is turned into a machine and stitch (overlocker, coverstitch, sewing machine with zigzag/stretch stitch/twin needle) from the spec option `machines`.

### Changed
- **Cut-on-fold edges**: every fold edge now carries the standard bracket symbol (two arrows pointing at the fold, "PLACE ON FOLD") instead of a text-only label. It is sized to the edge, so short fold edges such as a doll waistband get "ON FOLD"/"FOLD" in a smaller font instead of text running off the piece, and it keeps clear of fold-over lines and the grainline; the label block no longer covers it.
- The sewing instructions explain how to cut the pieces marked "on fold" for the layout used (on the fabric fold, or opened out on a single layer), and the cutting layout marks opened-out fold pieces "(unfolded)".

### Added
- **Your machines** (`--machines sewing,overlocker,coverstitch,…`, spec `machines`, workshop file via
  `profiles.py machines set …`, or per profile): the skill asks which machines you sew with (sewing machine
  with zigzag or straight stitch only, stretch stitch, twin needle, overlocker, coverstitch) and adapts the
  pattern to them. Knit seams on the overlocker get 7.5 mm seam allowance, woven seams on a
  straight-stitch-only machine 15 mm for French seams; every seam and hem step names your machine and
  stitch, and the instructions get a "Your machines" table with stitch settings and needles per kind of
  step. `machines.method()` / `tool_for()` give the machine and stitch per step as data.
- Validation check for every cut-on-fold edge: straight, no seam allowance, neighbouring edges at 90° (no peak or dip at the centre once unfolded), on grain.

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
