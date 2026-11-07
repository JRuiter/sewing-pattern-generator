### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 77.2 cm | 77.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 59.2 cm | 59.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 20.2 cm | 20.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 24.6 cm | 24.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket opening: front leg ↔ pocket bag | 12.5 cm | 12.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag seam: pocket bag ↔ side panel | 24.7 cm | 24.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Pocket bag ↔ side panel at the side seam | 5.2 cm | 5.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 79.7 cm | 79.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 32.4 cm | 22.7 cm = 70 % | -97.2 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.5° | +0.5° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband at the side panel | 90° | 90.0° | +0.0° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 82.5 cm | 82.5 cm | +0.0 % | ✅ OK | body 75.0 cm + +10 % ease |
| Measurements | Top edge fits over the hip | ≥ 76.5 cm | 91.6 cm | +151.2 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 16.8 cm – 26.6 cm | 21.0 cm | +0.0 mm | ✅ OK | body rise 19.5 cm |
| Measurements | Inseam length plausible | 46.6 cm – 72.2 cm | 64.7 cm | +0.0 mm | ✅ OK | body inseam 64.5 cm |
| Measurements | Foot fits through the leg opening | ≥ 27.3 cm | 33.6 cm | +62.3 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Side panel (outer pocket bag): outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Side panel (outer pocket bag): grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Inner pocket bag: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Inner pocket bag: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric or cotton jersey |
| Geometry | Waistband (elastic): outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Waistband (elastic): grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Leg cuff: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Leg cuff: grainline & cutting | present | cut 2 |  | ✅ OK | Rib knit |
| Geometry | Waistband (elastic): cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.0° off 90° |  | ✅ OK | Centre front |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 38 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 825}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 82.5 cm | hip × (1 + 10 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 20.1 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 21.1 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 4.1 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 8.3 cm | 10 % of hip_width |  |
| `rise` | 18.0 cm | (side length − inseam) + seat ease − waistband height |  |
| `inseam_finished` | 64.7 cm | inseam − allowance to the floor + blousing |  |
| `hem_width` | 32.4 cm | cuff length / cuff stretch ratio |  |