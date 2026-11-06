### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 57.1 cm | 57.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 38.6 cm | 38.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 20.3 cm | 20.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 23.7 cm | 23.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket opening: front leg ↔ pocket bag | 12.3 cm | 12.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag seam: pocket bag ↔ side panel | 21.4 cm | 21.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag ↔ side panel at the side seam | 3.6 cm | 3.6 cm | +0.0 mm | ✅ OK |  |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.8° | +0.8° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband at the side panel | 90° | 90.0° | +0.0° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 65.0 cm | 65.0 cm | -0.0 % | ✅ OK | body 57.0 cm + +14 % ease |
| Measurements | Top edge fits over the hip | ≥ 58.1 cm | 62.2 cm | +40.4 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 11.8 cm – 20.9 cm | 18.5 cm | +0.0 mm | ✅ OK | body rise 17.0 cm |
| Measurements | Inseam length plausible | 28.9 cm – 44.8 cm | 38.5 cm | +0.0 mm | ✅ OK | body inseam 40.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 20.8 cm | 29.9 cm | +91.1 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm; Waistband seam: 3.5 cm |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm; Waistband seam: 3.5 cm |
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

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 650}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 65.0 cm | hip × (1 + 14 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 15.7 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 16.7 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 3.2 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 6.5 cm | 10 % of hip_width |  |
| `rise` | 18.5 cm | (side length − inseam) + seat ease |  |
| `inseam_finished` | 38.5 cm | inseam − allowance to the floor |  |
| `hem_width` | 29.9 cm | leg opening for fit 'normal' |  |