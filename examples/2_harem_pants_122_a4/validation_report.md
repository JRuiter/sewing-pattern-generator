### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 66.0 cm | 66.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 41.7 cm | 41.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 26.9 cm | 26.9 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 31.3 cm | 31.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 83.0 cm | 83.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 28.5 cm | 20.0 cm = 70 % | -85.5 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.9° | +0.9° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.1° | +0.1° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 85.8 cm | 85.8 cm | +0.0 % | ✅ OK | body 66.0 cm + +30 % ease |
| Measurements | Top edge fits over the hip | ≥ 67.3 cm | 95.4 cm | +281.1 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 14.6 cm – 31.4 cm | 27.3 cm | +0.0 mm | ✅ OK | body rise 18.0 cm, harem drop 7.3 cm |
| Measurements | Inseam length plausible | 39.0 cm – 60.5 cm | 55.5 cm | +0.0 mm | ✅ OK | body inseam 54.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 24.1 cm | 29.5 cm | +54.8 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
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

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 858}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 85.8 cm | hip × (1 + 30 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 20.9 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 21.9 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 4.3 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 8.6 cm | 10 % of hip_width |  |
| `rise` | 24.3 cm | (side length − inseam) + seat ease + harem drop − waistband height |  |
| `inseam_finished` | 48.2 cm | inseam − allowance to the floor − harem drop + blousing |  |
| `hem_width` | 28.5 cm | cuff length / cuff stretch ratio |  |