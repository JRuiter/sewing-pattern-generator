# Changelog

All notable changes to this skill are listed here. Versions follow [semantic versioning](https://semver.org/).

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
