### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 94.3 cm | 94.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 76.0 cm | 76.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 20.1 cm | 20.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 25.9 cm | 25.9 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge (stretched) | 80–92 % of 85.4 cm | 68.3 cm = 80 % | -170.8 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 89.9° | -0.1° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.5° | +0.5° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.1° | +0.1° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 89.7 cm | 89.7 cm | +0.0 % | ✅ OK | body 98.0 cm + -8 % ease |
| Measurements | Top edge fits over the hip | ≥ 100.0 cm | 116.1 cm | +161.8 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 20.2 cm – 32.0 cm | 26.5 cm | +0.0 mm | ✅ OK | body rise 26.0 cm |
| Measurements | Inseam length plausible | 56.4 cm – 87.4 cm | 75.5 cm | +0.0 mm | ✅ OK | body inseam 78.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 31.8 cm | 32.0 cm | +2.4 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Wide yoga waistband: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Wide yoga waistband: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Front leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Back leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Wide yoga waistband: cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.0° off 90° |  | ✅ OK | Centre front |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 30 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 897}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 89.7 cm | hip × (1 + -8 % ease) |  |
| `front_back_offset` | 1.0 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 21.4 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 23.4 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 3.6 cm | 4 % of hip_width |  |
| `back_crotch_extension` | 7.2 cm | 8 % of hip_width |  |
| `rise` | 18.2 cm | (side length − inseam) + seat ease − waistband height |  |
| `inseam_finished` | 75.5 cm | inseam − allowance to the floor |  |
| `hem_width` | 23.5 cm | leg opening for fit 'slim' |  |