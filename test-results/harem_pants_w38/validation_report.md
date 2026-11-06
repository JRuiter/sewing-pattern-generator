### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 95.5 cm | 95.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 60.9 cm | 60.9 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 38.4 cm | 38.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 45.2 cm | 45.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge | 122.7 cm | 122.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Leg cuff ↔ leg opening (stretched) | 70–85 % of 37.6 cm | 26.3 cm = 70 % | -112.9 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 90.0° | -0.0° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.6° | +0.6° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.0° | +0.0° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 127.4 cm | 127.4 cm | +0.0 % | ✅ OK | body 98.0 cm + +30 % ease |
| Measurements | Top edge fits over the hip | ≥ 100.0 cm | 141.2 cm | +411.9 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 20.2 cm – 42.0 cm | 38.7 cm | +0.0 mm | ✅ OK | body rise 26.0 cm, harem drop 10.1 cm |
| Measurements | Inseam length plausible | 56.4 cm – 87.4 cm | 79.6 cm | +0.0 mm | ✅ OK | body inseam 78.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 31.8 cm | 39.0 cm | +72.3 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
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

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 1274}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 127.4 cm | hip × (1 + 30 % ease) |  |
| `front_back_offset` | 1.0 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 30.9 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 32.9 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 6.4 cm | 5 % of hip_width |  |
| `back_crotch_extension` | 12.7 cm | 10 % of hip_width |  |
| `rise` | 34.5 cm | (side length − inseam) + seat ease + harem drop − waistband height |  |
| `inseam_finished` | 69.6 cm | inseam − allowance to the floor − harem drop + blousing |  |
| `hem_width` | 37.6 cm | cuff length / cuff stretch ratio |  |