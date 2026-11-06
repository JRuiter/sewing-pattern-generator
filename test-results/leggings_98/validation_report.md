### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 50.2 cm | 50.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Inseam front ↔ back | 38.8 cm | 38.8 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Front crotch seam (left ↔ right piece) | 12.4 cm | 12.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Back crotch seam (left ↔ right piece) | 15.7 cm | 15.7 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Waistband ↔ pants top edge (stretched) | 80–92 % of 49.6 cm | 39.7 cm = 80 % | -99.1 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Centre front ↔ waistband | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Centre back ↔ waistband | 90° | 89.9° | -0.1° | ✅ OK |  |
| Angles/transitions | Crotch ↔ inseam (front + back) | 180° | 180.9° | +0.9° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem front | 90° | 90.1° | +0.1° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Inseam ↔ hem back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam back | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband back | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Side seam ↔ waistband (front + back) | 180° | 180.2° | +0.2° | ✅ OK |  |
| Measurements | Hip circumference pattern = body + ease | 52.2 cm | 52.2 cm | +0.0 % | ✅ OK | body 57.0 cm + -8 % ease |
| Measurements | Top edge fits over the hip | ≥ 58.1 cm | 67.4 cm | +92.8 mm | ✅ OK | top edge incl. usable stretch ≥ hip |
| Measurements | Front rise plausible | 11.8 cm – 20.9 cm | 17.4 cm | +0.0 mm | ✅ OK | body rise 17.0 cm |
| Measurements | Inseam length plausible | 28.9 cm – 44.8 cm | 38.5 cm | +0.0 mm | ✅ OK | body inseam 40.0 cm |
| Measurements | Foot fits through the leg opening | ≥ 20.8 cm | 20.9 cm | +1.5 mm | ✅ OK | heel-instep circumference ≈ 1.35 × ankle |
| Geometry | Front leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm |
| Labels | Front leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Back leg: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.5 cm |
| Labels | Back leg: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Wide yoga waistband: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included |
| Labels | Wide yoga waistband: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Front leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Back leg: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Labels | Front leg: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |
| Labels | Back leg: notches | on the cutting line | 6 notch mark(s) |  | ✅ OK |  |

**Result:** 29 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"hip_width": 522}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `hip_width` | 52.2 cm | hip × (1 + -8 % ease) |  |
| `front_back_offset` | 0.5 cm | front quarter narrower, back quarter wider by this amount |  |
| `front_width` | 12.5 cm | hip_width / 4 − front_back_offset |  |
| `back_width` | 13.5 cm | hip_width / 4 + front_back_offset |  |
| `front_crotch_extension` | 2.1 cm | 4 % of hip_width |  |
| `back_crotch_extension` | 4.2 cm | 8 % of hip_width |  |
| `rise` | 11.4 cm | (side length − inseam) + seat ease − waistband height |  |
| `inseam_finished` | 38.5 cm | inseam − allowance to the floor |  |
| `hem_width` | 15.4 cm | leg opening for fit 'slim' |  |