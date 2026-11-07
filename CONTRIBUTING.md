# Contributing

Thanks for helping to improve the sewing-pattern generator. This guide covers the development setup,
the checks every change has to pass, and – in most detail – how to add a new garment module.

## Development setup

Python ≥ 3.10.

```bash
pip install -r requirements-dev.txt
pre-commit install            # optional: runs ruff on every commit
```

| Command | What it does |
|---|---|
| `python -m pytest tests -m "not slow"` | quick run (291 of 306 tests, ~4 min), skips PDF rendering and the photo round trips |
| `python -m pytest tests` | full suite, as in CI (306 tests, ~7 min; the A4 overlap test needs `pdftoppm` from poppler) |
| `ruff check scripts tests tools` | lint (config in `pyproject.toml`) |
| `mypy` | type check (baseline config in `pyproject.toml`) |
| `python tools/build_skill_zip.py` | build the installable skill ZIP into `dist/` |

CI runs ruff, mypy and the full test suite with coverage on every pull request.

### Code conventions

- All lengths inside the code are **millimetres**; measurements from the user are converted from cm in
  `measurements.py`.
- Scripts are run directly from `scripts/` (Claude skill layout, no installable package). Modules import
  each other as top-level modules (`import geometry as G`, `from pattern import Piece`).
- Output shown to the end user (labels on the pattern, reports, sewing instructions) follows the
  language of the skill; code, comments and docs are in English.
- Never weaken a validation check or skip a test to make a pattern pass. Fix the draft instead.

### Releases

Bump `version` in `pyproject.toml`, merge to `main`, then tag: `git tag v1.1.0 && git push --tags`
(or run the *Release* workflow manually on `main`, which creates the tag itself). The
*Release* workflow runs the tests, checks that the tag matches the version, and attaches
`<skill-name>-<version>.zip` to a GitHub release.

## Adding a garment module

A garment module is one file in `scripts/garments/` that turns body measurements and options into a
`Pattern`. Everything downstream – validation, layout, PDF/SVG rendering, cutting layout, fabric
consumption and sewing instructions – works on that `Pattern` and needs no changes.

### 1. The module contract

| Name | Required | Purpose |
|---|---|---|
| `DEFAULTS: dict` | yes | default options; user options override them |
| `draft(measures: dict, options: dict \| None) -> Pattern` | yes | builds the pattern; `measures` are body measurements in mm (see `measurements.py` for the keys: `height`, `chest`, `waist`, `hip`, `head`, `inseam`, …) |
| `FINISHED_LABELS: dict` | recommended | `key → (label, kind)`: display names for the keys of `pattern.finished` in the finished-measure table and the photo-mode-B deviation report. `kind` (`"length"` or `"width"`) documents the key; the tolerances themselves (±1 cm lengths, ±2 % widths) come from `WIDTH_KEYS` in `scripts/reverse/fit.py` |
| `sewing_steps(pattern) -> list[str]` | recommended | numbered sewing steps (Markdown) appended to the generic cutting instructions |
| `finished_measures(pattern) -> dict` | optional | needed only if the module supports reverse engineering in photo mode B |

Finally register the module in `scripts/garments/__init__.py` (`GARMENTS` maps the module name to a
short description).

### 2. Pieces and edges (`scripts/pattern.py`)

- A `Piece` is a closed, **counter-clockwise** sequence of named `Edge`s. Edges describe the **seam line**
  (net outline); the cut line is computed from each edge's `sa` (seam allowance in mm).
- Consecutive edges must meet (gap ≤ 0.5 mm) – `Piece.check_closed()` and the validation check this.
- Fold edges: `Edge(..., sa=0, fold=True)`; they are drawn dash-dotted and the cutting layout unfolds them.
- Hems and casings whose allowance is folded back: `Edge(..., turned=True)`. Their corners are mirrored
  at the fold line so the folded allowance matches a tapered neighbouring seam.
- Every piece needs a `grain` (two points for the grainline arrow), a `cut_count`, `mirror` (cut as a
  mirrored pair) and a `fabric` (main fabric, rib, lining …; this groups the cutting layout).
- `notches`, `marks` (pocket placement, fold lines, elastic casing) and `info` lines are optional.
  A `Notch` sits on the seam line; rendering and DXF project it onto the cutting line (bisector at
  corners), so a notch at an edge end (`s=-1`) is fine.
- Record important derived values with `construction.Construction`
  (`C.val("rise", value, "formula text")`) and set `pat.construction = C.rows()`: they appear in the
  report and can be overridden by the user with the option `construction`.
- `rect_piece(...)` builds rectangular pieces (bands, cuffs, pockets) with one call.

Geometry helpers live in `scripts/geometry.py`: `G.P`, `G.line`, `G.tangent_curve`, `G.join`,
`G.length`, `G.point_at`, offsets and intersections. Prefer smooth Bézier curves with defined tangents
at the ends so joined corners pass the smoothness check.

### 3. Declare what has to be validated (`scripts/validate.py`)

The `Pattern` carries three lists that the validation turns into the report table. Without them a
module "passes" without proving anything, so declare every seam that is sewn together.

**`seams`** – pairs of edge sums, each entry `(piece_key, edge_name, count)`:

```python
dict(name="Side seam front ↔ back", a=[("front", "side", 1)], b=[("back", "side", 1)], type="equal")
dict(name="Cuff ↔ sleeve hem (stretched)", a=[("sleeve", "hem", 2)], b=[("cuff", "bottom", 1)],
     type="ratio", lo=0.75, hi=0.85)          # b / a must be within lo..hi
dict(name="Sleeve cap ease", a=[("front", "armhole", 1), ("back", "armhole", 1)],
     b=[("sleeve", "cap", 1)], type="ease", lo=5, hi=15)   # b − a in mm
```

`equal` allows ±2 mm. Use the `ease` helpers (`ease.band_ratio_range`, `ease.cap_ease_range_mm`) for
the ranges instead of magic numbers.

**`corners`** – angles where edges meet: `target=90` for centre/side seams that must be square,
`target=180` where two edges of the same piece must join smoothly. For corners that are only right
angles once two pieces are sewn together, use `sum=[(piece, a, b), …]`.

**`checks`** – value checks: `kind="circ"` (finished circumference = body + ease, ±1 %),
`kind="min"` (e.g. the opening fits over head/foot, including stretch) and `kind="range"`
(plausibility, defaults to a warning).

The geometric checks (closed outline, no self-intersection, seam allowance on every non-fold edge,
grainline present, turned allowances lie flat, notches on the cutting line) run automatically for
every piece.

### 4. Minimal example

`scripts/garments/loop.py` is the smallest complete module (one rectangle, two seams, one corner, one
value check) and the best starting point; `beanie.py` adds a curved edge and an optional second piece.
A new module looks like this:

```python
"""Headband: a rectangle folded lengthwise and closed into a ring."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Mark, Pattern, rect_piece

DEFAULTS = dict(fabric="jersey", stretch=None, width=100.0, sa=7.0)
FINISHED_LABELS = {"circ": ("Circumference", "width"), "width": ("Width (double layer)", "length")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    head = measures["head"]
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    circ = head * 0.85                                  # negative ease for knits
    w = o["width"]
    p = rect_piece("band", "Headband", circ, 2 * w, sa=o["sa"], cut_count=1,
                   names=("bottom", "right", "top", "left"), grain_vertical=False)
    p.marks.append(Mark(G.line(G.P(0, w), G.P(circ, w)), "fold", "Fold"))
    seams = [dict(name="Ring seam", a=[("band", "right", 1)], b=[("band", "left", 1)], type="equal")]
    corners = [dict(name="Corner bottom right", piece="band", a="bottom", b="right", target=90)]
    checks = [dict(name="Fits over the head", kind="min", value=circ * (1 + stretch / 100),
                   target=head * 1.02, note="incl. stretch")]
    pat = Pattern("headband", "Headband", "", [p], dict(measures), o,
                  seams=seams, corners=corners, checks=checks)
    pat.finished = dict(circ=circ, width=w)
    return pat


def sewing_steps(pat):
    return ["**Ring:** fold right sides together crosswise and sew the short edges.",
            "**Fold:** fold lengthwise, wrong sides together, and finish the raw edges together."]
```

Then: `python scripts/generate.py --garment headband --size 122 --format a4 --out out/headband`.

### 5. Wire it up

- [ ] `scripts/garments/__init__.py`: add to `GARMENTS`.
- [ ] `tests/test_validate.py`: add one or more entries to `CASES` (default options plus the important
      variants). They are drafted and validated in children's and adult sizes.
- [ ] Add tests for module-specific checks (e.g. a broken variant that must fail validation).
- [ ] `scripts/photo_analyze.py`: map the garment type and features to the module so photo mode A
      offers it; remove it from the "not covered" texts.
- [ ] `SKILL.md`: module table, trigger words in the description, limits section.
- [ ] `README.md`: garments table.
- [ ] Generate a validation report and preview for three sizes into `test-results/`
      (`python scripts/generate.py … --format roll610 --out <folder>`; keep `validation_report.md` and the
      preview PNG) and link them from its overview page.
- [ ] Look at the preview PNGs yourself: all pieces present, nothing overlapping, labels readable.

### 6. Pull request checklist

- [ ] `ruff check scripts tests tools`, `mypy` and `python -m pytest tests` pass locally.
- [ ] No validation check was loosened to make the new pattern pass.
- [ ] Examples or test results regenerated if the output of existing modules changed.
