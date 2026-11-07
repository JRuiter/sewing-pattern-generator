### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 51.8 cm | 51.8 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 30.0 cm | 30.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 24.1 cm | 24.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 28.1 cm | 28.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 71.3 cm | 71.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 24.6 cm | 17.2 cm = 70 % | -73.9 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 181.2° | +1.2° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.1° | +0.1° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 74.1 cm | 74.1 cm | +0.0 % | ✅ OK | body 57.0 cm + +30 % ease |
| Measurements | Top edge fits over the hip | ≥ 58.1 cm | 82.0 cm | +238.7 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 11.8 cm – 26.7 cm | 24.8 cm | +0.0 mm | ✅ OK | body rise 17.0 cm, harem drop 5.9 cm |
| Measurements | Inseam length plausible | 28.9 cm – 44.8 cm | 40.9 cm | +0.0 mm | ✅ OK | body inseam 40.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 20.8 cm | 25.5 cm | +47.3 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
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

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 741}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 74.1 cm | hip × (1 + 30 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 18.0 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 19.0 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 3.7 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 7.4 cm | 10 % of hip_width |  |
| `rise` | 21.8 cm | (side length − inseam) + seat ease + harem drop − waistband height |  |
| `inseam_finished` | 35.0 cm | inseam − allowance to the floor − harem drop + blousing |  |
| `hem_width` | 24.6 cm | cuff length / cuff stretch ratio |  |