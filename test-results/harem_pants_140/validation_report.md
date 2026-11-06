### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 77.4 cm | 77.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 50.6 cm | 50.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 29.8 cm | 29.8 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 34.6 cm | 34.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 94.7 cm | 94.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 32.4 cm | 22.7 cm = 70 % | -97.2 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.8° | +0.8° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.1° | +0.1° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 97.5 cm | 97.5 cm | +0.0 % | ✅ OK | body 75.0 cm + +30 % ease |
| Measurements | Top edge fits over the hip | ≥ 76.5 cm | 108.9 cm | +323.7 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 16.8 cm – 35.0 cm | 29.9 cm | +0.0 mm | ✅ OK | body rise 19.5 cm, harem drop 8.4 cm |
| Measurements | Inseam length plausible | 46.6 cm – 72.2 cm | 66.4 cm | +0.0 mm | ✅ OK | body inseam 64.5 cm |
| Measurements | Foot fits through the leg opening | ≥ 27.3 cm | 33.6 cm | +62.3 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Waistband (elastic): outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Waistband (elastic): grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Leg cuff: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Leg cuff: grainline & cutting | present | cut 2 |  | ✅ OK | Rib knit |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 30 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 975}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 97.5 cm | hip × (1 + 30 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 23.9 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 24.9 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 4.9 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 9.8 cm | 10 % of hip_width |  |
| `rise` | 26.9 cm | (side length − inseam) + seat ease + harem drop − waistband height |  |
| `inseam_finished` | 58.0 cm | inseam − allowance to the floor − harem drop + blousing |  |
| `hem_width` | 32.4 cm | cuff length / cuff stretch ratio |  |