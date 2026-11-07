## Reverse engineering: result

Detected module: **Joggers**, fit **normal**, estimated size ≈ 116

**Pieces:**
- Front leg: cut 2 (mirrored pair)
- Back leg: cut 2 (mirrored pair)
- Waistband (elastic): cut 1 on fold (on fold)
- Leg cuff: cut 2
**Seams:**
- Side seam front ↔ back: Front leg.Side seam ↔ Back leg.Side seam
- Inseam front ↔ back: Front leg.Inseam ↔ Back leg.Inseam
- Front crotch seam (left ↔ right piece): Front leg.Crotch seam ↔ Front leg.Crotch seam
- Back crotch seam (left ↔ right piece): Back leg.Crotch seam ↔ Back leg.Crotch seam
- Waistband ↔ pants top edge: Front leg.Waistband seam + Back leg.Waistband seam ↔ Waistband (elastic).Seam edge
- Leg cuff ↔ leg opening (stretched): Front leg.Cuff seam + Back leg.Cuff seam ↔ Leg cuff.Seam edge

### Deviation report (target = measured, actual = reconstructed pattern)

| Measurement | Target | Actual | Δ | Tolerance | Result |
|---|---|---|---|---|---|
| Hip width | 69.2 cm | 69.2 cm | -0.0 cm (-0.0 %) | ± 2 % (1.4 cm) | ✅ |
| Thigh width | 44.1 cm | 44.0 cm | -0.1 cm (-0.3 %) | ± 2 % (0.9 cm) | ✅ |
| Leg width at mid-leg | 34.3 cm | 34.5 cm | +0.2 cm (+0.5 %) | ± 2 % (0.7 cm) | ✅ |
| Leg opening | 19.4 cm | 19.4 cm | -0.0 cm (-0.2 %) | ± 2 % (0.4 cm) | ✅ |
| Waistband relaxed | 49.4 cm | 49.4 cm | +0.0 cm (+0.0 %) | ± 2 % (1.0 cm) | ✅ |
| Front rise | 19.1 cm | 19.1 cm | -0.0 cm | ± 1.0 cm | ✅ |
| Inseam | 51.2 cm | 51.3 cm | +0.0 cm | ± 1.0 cm | ✅ |
| Outseam | 70.3 cm | 70.4 cm | +0.0 cm | ± 1.0 cm | ✅ |
| Waistband height | 3.1 cm | 3.1 cm | +0.0 cm | ± 1.0 cm | ✅ |
| Cuff height | 5.0 cm | 5.0 cm | +0.0 cm | ± 1.0 cm | ✅ |

**Result:** all measurements within tolerance.

### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 62.3 cm | 62.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 46.4 cm | 46.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 17.8 cm | 17.8 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 21.6 cm | 21.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 66.4 cm | 66.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 27.7 cm | 19.4 cm = 70 % | -83.0 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.7° | +0.7° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.1° | +0.1° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 69.2 cm | 69.2 cm | +0.0 % | ✅ OK | target from measurement/override |
| Measurements | Top edge fits over the hip | ≥ 64.3 cm | 76.4 cm | +120.9 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 13.9 cm – 23.2 cm | 19.1 cm | +0.0 mm | ✅ OK | body rise 17.5 cm |
| Measurements | Inseam length plausible | 36.8 cm – 57.1 cm | 51.3 cm | +0.0 mm | ✅ OK | body inseam 51.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 23.0 cm | 28.7 cm | +56.9 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Waistband (elastic): outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Waistband (elastic): grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Leg cuff: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Leg cuff: grainline & cutting | present | cut 2 |  | ✅ OK | Rib knit |
| Geometry | Waistband (elastic): cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.0° off 90° |  | ✅ OK | Centre front |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 31 OK, 0 warning(s), 0 error(s): the pattern is sewable.