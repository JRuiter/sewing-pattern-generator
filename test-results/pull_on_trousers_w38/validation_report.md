### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 103.7 cm | 103.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 75.7 cm | 75.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 31.0 cm | 31.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 37.1 cm | 37.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket opening: front leg ↔ pocket bag | 18.6 cm | 18.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag seam: pocket bag ↔ side panel | 34.0 cm | 34.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag ↔ side panel at the side seam | 6.2 cm | 6.2 cm | +0.0 mm | ✅ OK |  |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.4° | +0.4° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband at the side panel | 90° | 90.0° | +0.0° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 111.7 cm | 111.7 cm | +0.0 % | ✅ OK | body 98.0 cm + +14 % ease |
| Measurements | Top edge fits over the hip | ≥ 100.0 cm | 107.0 cm | +70.8 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 20.2 cm – 32.0 cm | 28.0 cm | +0.0 mm | ✅ OK | body rise 26.0 cm |
| Measurements | Inseam length plausible | 56.4 cm – 87.4 cm | 75.5 cm | +0.0 mm | ✅ OK | body inseam 78.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 31.8 cm | 51.4 cm | +196.4 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm; Waistband seam: 4.5 cm |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm; Waistband seam: 4.5 cm |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Side panel (outer pocket bag): outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Side panel (outer pocket bag): grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Inner pocket bag: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Inner pocket bag: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric or cotton jersey |
| Geometry | Front leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem, Waistband seam: corners mirrored at the fold line |
| Geometry | Back leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem, Waistband seam: corners mirrored at the fold line |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 33 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 1117}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 111.7 cm | hip × (1 + 14 % ease) |  |
| `front_back_offset` | 1.0 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 26.9 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 28.9 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 5.6 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 11.2 cm | 10 % of hip_width |  |
| `rise` | 28.0 cm | (side length − inseam) + seat ease |  |
| `inseam_finished` | 75.5 cm | inseam − allowance to the floor |  |
| `hem_width` | 51.4 cm | leg opening for fit 'normal' |  |