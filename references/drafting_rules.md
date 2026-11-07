# Drafting rules

Original parametric constructions based on the generally known principles of garment
drafting (basic block from body measurement + ease, right angles at centre and side
seams, curves tangent at seam ends). No patterns from books or magazines are rebuilt.
All measurements in mm; the formulas are in the code under `scripts/garments/`.

Symbols: `H` hip circumference, `B` chest circumference, `BH` body height, `IL` inseam
length, `SL` side length, `k = BH / 1220` (scaling of small pieces, kids' size 122 = 1,
limited to 0.75–1.45).

## 1. General rules

- **Coordinates:** x to the right, y up, edges counter-clockwise, each edge with its own
  seam allowance. The cutting line is created by offsetting each edge by its seam
  allowance; corners are mitred (intersection point) and bevelled at sharp angles.
- **User allowances** (`scripts/allowance.py`): `seam_allowance_mm` replaces the module
  default `sa` (10 mm; beanie 7 mm), `hem_allowance_mm` the hem default `hem_sa`. Allowances
  derived from `sa` (e.g. neckline = 0.7 × sa) scale with it. Construction allowances
  (elastic casing, hood/pocket facing, narrow circle hem) stay fixed. Range 0–30 mm (hems
  0–60 mm). With `seam_allowance: "none"` / `0` the pattern is drafted with the defaults,
  then every allowance is moved to `Edge.sa_hint` and set to 0: cutting line = seam line,
  labels say "NO seam allowance included: add …", validation accepts the missing allowance.
- **Turned allowances** (hems, casings, `Edge.turned`): the allowance is folded back onto
  the piece, so its corners are **mirrored** at the fold line instead of mitred. On a leg
  or sleeve that narrows towards the hem the hem allowance therefore flares out again;
  folded up, it lies exactly under the side seam allowance instead of pulling or
  sticking out. Where a mirror is not geometrically possible the corner falls back to
  the mitre and validation warns.
- **Notches** are defined on the seam line and projected onto the cutting line along the
  edge normal; a notch at a corner (≤ 1.5 mm from an edge end, e.g. underarm, crotch
  point) is projected along the **bisector** of the two edges so it meets the mitred
  corner. Shapes: slit (default), T (slit with a cross bar at the seam line), V (cut into
  the allowance, for cutting machines/projectors). Double notches (back) are 3 mm apart.
- **Construction values:** every module records its derived values with name and formula
  (`scripts/construction.py`); they appear in the validation report and can be overridden
  with the option `construction` (mm). Pants: `hip_width`, `front_back_offset`,
  `front_width`, `back_width`, `front_crotch_extension`, `back_crotch_extension`, `rise`,
  `inseam_finished`, `hem_width`. Tops: `chest_width`, `neck_width_half`,
  `front_neck_depth`, `back_neck_depth`, `shoulder_length`, `armhole_depth`, `body_length`.
- **Seam allowances:** 1.0 cm standard (overlocker/sewing machine), pants hem 2.5 cm,
  shirt hem 2.0 cm, neckline 0.7 cm, fold edges 0.
- **Curves** are cubic Bézier curves with given end tangents. At every corner where two
  pieces are sewn into a continuous edge (e.g. shoulder + armhole, left + right crotch
  seam) the angles must add up to 180°; at centre/fold edges every curve meets the edge
  at a right angle.
- **Ease** (`scripts/ease.py`), as a share of the body circumference:

| Fit | Chest woven | Chest knit* | Hip woven | Hip knit* |
|---|---|---|---|---|
| slim | +6 % | ±0 (negative at ≥ 40 % stretch, down to −10 %) | +6 % | −4 … −12 % (leggings) |
| normal | +14 % | +9 % | +14 % | +10 % |
| wide | +22 % | +17 % | +22 % | +18 % |
| oversized | +32 % | +27 % | +30 % | +26 % |
| harem | – | – | +34 % | +30 % |

  \* at 30 % stretch; every 10 % more stretch means 1 % less ease.

- **Rib ratio** (rib length / edge it is sewn to): rib knit 0.85 at 50 % stretch down to
  0.70 at 80 % stretch; jersey strips 0.80–0.92.
- **Sleeve cap ease:** jersey 0–5 mm, sweat/fleece 0–8 mm, woven 10–25 mm. The cap height
  is found by bisection so that the target amount (40 % of the range) is reached.

## 2. Pants (`pants_basic`)

1. **Hip width** `Hc = H × (1 + ease)`; front `Hc/4 − d`, back `Hc/4 + d`
   (d = 5 mm kids, 10 mm adults).
2. **Crotch extension:** front 5 % of Hc, back 10 % (slim: 4 % / 8 %); adjustable via
   `fork_factor` (reverse engineering).
3. **Rise** `R = (SL − IL) + seat allowance + harem drop − waistband height`;
   seat allowance 15 mm kids / 20 mm adults (slim ×0.25, wide ×1.3, oversized ×1.6),
   harem drop 6 % of body height. Hip line at 0.55 × R below the top edge.
4. **Leg length** from the crotch line: `IL − 15/25 mm − drop + blousing`; with cuffs
   15 mm × k (harem 30 mm × k) blousing above the cuff.
5. **Leg opening:** with cuffs `max(1.12 × ankle, ankle + 15 mm) / rib ratio`;
   without cuffs: normal 0.46 × Hc, wide 0.62 × Hc, harem 0.40 × Hc, slim = ankle
   (+8 % below 50 % stretch). Front/back leg ±2 d around half.
6. **Leg lines:** clamped cubic splines x(y) from the crotch line to the hem; a knee point
   (half leg length) only for slim fit or when `knee_total` is set.
7. **Front crotch curve:** from the hip line (centre front vertical) to the crotch point;
   it meets the **inseam at a right angle**.
8. **Back:** centre back moved inwards at the top by 15/25 mm and raised by 15/25 mm
   (slim 20/35); the back crotch point is lowered by bisection so that **back inseam =
   front inseam**. Top edge tangential, at a right angle to centre back. The back side
   seam is adjusted at the top so that **both side seams have the same length**.
9. **Waistband:** elastic casing as a folded fabric strip, length = top edge of the pants
   (ungathered), cut on the fold (half length); elastic ≈ 0.9 × waist.
   Alternatives: rib (ratio see above), yoga waistband (60 mm × k), tunnel (turned down).
10. **Pockets:** side pocket (`side`: slanted opening from the top edge to the side seam,
    side panel + pocket bag; dropped for slim fit), back patch pocket (`back_patch`). Pocket opening at the front: 0.28 × front width, depth at the side seam
    0.62 × R (95–170 mm). **Cargo pocket** (`pockets: [cargo]`): patch pocket on the front
    thigh next to the side seam, top 12 % of the leg length + 4.5 cm × k below the crotch
    line, about 15 × 17.5 cm × k (shrunk until it fits inside the leg), box pleat 2 cm × k
    (`cargo_pleat`), flap (`cargo_flap`, 4 pieces).
11. **Leg shape** (`leg_shape`, long legs without cuffs): the knee point (45 % of the leg
    length) gets the width of the straight leg there (≥ knee × (1 + ease)); below it
    `tapered` = 80 % of the narrower of knee and straight opening (foot must fit through,
    ≥ 1.35 × ankle + 2 cm), `bootcut` / `flare` = knee width + `flare_cm` (defaults 6 / 16 cm
    × k, children × 0.6). Inseam and side seams are matched front ↔ back as usual.
12. **Shorts / knee length:** the leg opening is at least 92 % of the leg circumference at
    the crotch line. `turn_up` (cm) adds twice its height to the hem allowance and marks
    the hem edge and the turn-up fold.

**Parameters for reverse engineering:** `hip_total`, `fork_factor`, `front_rise_total`,
`inseam_total`, `opening_total`, `knee_total` (all can be overridden as options).

## 3. T-shirt / raglan (`tshirt_basic`)

1. **Chest width** `Ct = B × (1 + ease)`, quarter `q = Ct/4`.
2. **Neckline:** half width `nw = neck/5 + 15`; depth front `nw + 15/25`
   (V-neck +60), back 15/20. The neckline meets centre and shoulder at right angles. If
   the neckline (incl. stretch) does not fit over the head, it is widened automatically
   until the check "Neckline fits over the head" passes.
3. **Shoulder:** length = shoulder width (+15 mm wide, +4 % chest oversized),
   slope 17°.
4. **Armhole depth** `0.18 × Ct + 25` (+3 % Ct for wide/oversized); the armhole starts at
   a right angle to the shoulder and ends at a right angle to the side seam.
5. **Length** = back length + 0.13 × BH (tunic +0.12 × BH).
6. **Sleeve:** width = upper arm × (1 + 8/18/30/40 %); cap as a symmetric Bézier curve,
   cap height by bisection to the target ease. Short-sleeve underarm seam ≥ 35 mm
   (≥ 50 mm with cuffs). Front/back sleeve seams the same length, underarm corners 90°.
7. **Raglan:** the raglan lines from the neckline to the underarm are transferred rigidly
   to the sleeve; the sleeve neck is a curve at right angles to both raglan seams; the
   back raglan seam is brought to the same length by bisection.
8. **Neckband:** length = neckline × rib ratio, width 2 × band height.

## 4. Hoodie (`hoodie`)

T-shirt construction with fit "wide", sweat, rib cuffs at sleeves and hem.
**Hood:** height `0.58 × head + 25`, width `0.44 × head + 15`; the neck seam of the hood
is brought exactly to half the neckline length by bisection and meets the front edge at
a right angle (casing/facing 25 mm). Kangaroo pocket: 0.62 × q wide, slanted openings.

## 5. Skirt (`skirt`)

- **Gathered:** rectangles, width at top = max(1.6 × H, 1.25 × H), on the fold;
  elastic waistband.
- **A-line:** width at top 1.10 × H, side seam flared 12°; hem and waist meet centre and
  side seam at right angles (hem lower at the centre: `L × (1/cos α − 1)`).
- **Circle:** quarter circle on the fold; inner radius `r = top width / 2π`, outer radius
  `r + skirt length`. Pieces wider than the roll are tiled into strips.
- Lengths: mini, knee (side length − 0.285 × BH), midi, maxi.

## 5a. Dress (`dress`)

- **waist_seam:** the T-shirt bodice (all its rules) with body length = back length + 1 cm;
  its hem becomes the waist seam (seam allowance, not turned). The skirt comes from the
  skirt module with skirt length (waist → hem, as for skirts), without waistband; its top
  edge is solved iteratively so that it equals the bodice waist (A-line, circle) or the
  bodice waist × `gather` (gathered). Validation: waist seam bodice ↔ skirt equal, or as a
  ratio with the gather ratio limited to **1.0–2.5** (error outside); the waist seam incl.
  usable stretch must pass over the chest (pull-on dress). Optional elastic (0.95 × waist)
  in the waist seam, optional in-seam pockets (bag cut 4, opening 14 cm × k starting
  3 cm × k below the waist, marked with notches on the skirt side seams).
- **shirt_dress:** T-shirt lengthened to back length + skirt length; side seam curved from
  the underarm to the hem with an extra hem width of `flare_cm` (default ≥ 25 % of the
  chest width and ≥ 1.25 × hip with ease); the hem is curved (lower at the centre) so it
  meets the side seam at 90°. Check: width at hip level ≥ hip + 4 %.

## 6. Beanie (`beanie`) and loop scarf (`loop`)

- **Beanie:** width = head × 0.86 (knit with ≥ 30 % stretch, otherwise × 0.98),
  height 0.36 × head (slouch 0.48). 2 pieces with a round crown; the crown curve starts
  at a right angle at the side seam and runs horizontally over the centre. Optional brim
  (0.10 × head).
- **Loop:** rectangle, circumference 1.2 × head (single) or 2.6 × head (wrapped twice),
  height 0.17 × BH (adults 30 cm), folded in half along the height; circumference incl.
  half the stretch must be ≥ 1.1 × head.

## 7. Sewability validation (`scripts/validate.py`)

| Check | Rule |
|---|---|
| Seam pairs equal length | ± 2 mm (side seams, inseam, crotch, shoulder, sleeve seams, hood) |
| Rib ↔ edge | ratio within the range of the rib fabric (70–85 %, jersey up to 92 %) |
| Gathering | skirt ↔ waistband within the intended gathering amount |
| Sleeve cap ↔ armhole | ease within the fabric range (see above) |
| Corners | 90° or 180° (joined); OK ≤ 3°, warning ≤ 6°, otherwise error (joined corners +4° tolerance) |
| Circumferences | finished circumference = body measurement + ease, ± 1 % |
| Lengths | rise, inseam, sleeve length plausible for the body height |
| Head | neckline/waistband incl. stretch ≥ head or hip circumference |
| Geometry | outline closed, counter-clockwise, not self-intersecting; seam allowance on every non-fold edge measured with a normal ray |
| Labels | every piece has a grainline (inside the piece) and cutting information |
| Turned allowances | folded at the seam line, the allowance next to each corner lies on the neighbouring cutting line (≤ 0.5 mm, otherwise warning) |
| Notches | every notch mark starts on the cutting line |

An error (❌) blocks the print files.

## 8. Fit adjustments after a test garment (`scripts/adjust.py`)

Feedback from the toile is given either as a signed change of a finished measurement
(`{"hip": "+2cm"}`) or as a fit issue with an amount (`{"crotch_low": "1.5cm"}`). Units:
`mm`, `cm` (default), `in`. The garment is drafted once, the drafted construction value is
read and the garment is drafted again with value + Δ. Validation runs on the adjusted
pattern as usual. Explicit `construction` overrides win over adjustments.

**Pants (`pants_basic`)**

| Adjustment | Fit issues | Acts on |
|---|---|---|
| `hip` | `hip_tight`, `hip_loose` | `hip_width` (+Δ circumference) |
| `seat` | `seat_tight`, `seat_loose` | `back_crotch_extension` (+Δ/2 per leg) |
| `rise` | `crotch_low` (−), `crotch_tight` (+) | `rise` (front rise / crotch depth) |
| `inseam` | `legs_long`, `legs_short` | `inseam_finished` |
| `opening` | `opening_tight`, `opening_wide` | `hem_width` (leg opening) |
| `waist` | `waist_tight`, `waist_loose` | elastic length (relaxed waist) |

**Tops (`tshirt_basic`, `hoodie`, `dress` without `length`)**

| Adjustment | Fit issues | Acts on |
|---|---|---|
| `chest` | `chest_tight`, `chest_loose` | `chest_width` |
| `length` | `too_long`, `too_short` | `body_length` |
| `armhole` | `armhole_tight` (+), `armhole_low` (−) | `armhole_depth` |
| `shoulder` | `shoulders_wide` (−), `shoulders_narrow` (+) | `shoulder_length` |
| `neckline` | `neckline_gaping` (−), `neckline_tight` (+) | `neck_width_half` (per side) |
| `sleeve_length` | `sleeves_long`, `sleeves_short` | sleeve length |

The adjustments are stored in `options.adjustments` (pattern.json, project.json) and only
there: they are re-applied on every run, so "same as last time, one size up" keeps them.
The instructions show the finished measurements before and after.
