### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 25.1 cm | 25.1 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam front: front ↔ sleeve | 13.6 cm | 13.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam back: back ↔ sleeve | 16.2 cm | 16.2 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Sleeve seam (front ↔ back) | 32.6 cm | 32.6 cm | -0.8 mm | ✅ OK |  |
| Seam pairs | Neckband ↔ neckline (stretched) | 70–85 % of 41.3 cm | 28.9 cm = 70 % | -123.9 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Underarm: side seam ↔ raglan (body) | 90° | 90.8° | +0.8° | ✅ OK |  |
| Angles/transitions | Underarm: sleeve seam ↔ raglan (sleeve front) | 90° | 89.5° | -0.5° | ✅ OK |  |
| Angles/transitions | Neckline at centre front | 90° | 90.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Neckline at centre back | 90° | 89.5° | -0.5° | ✅ OK |  |
| Angles/transitions | Hem at centre front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | -0.0° | ✅ OK |  |
| Measurements | Chest circumference pattern = body + ease | 59.4 cm | 59.5 cm | +0.1 % | ✅ OK | body 55.0 cm + +8 % ease |
| Measurements | Neckline fits over the head | ≥ 50.0 cm | 52.0 cm | +20.3 mm | ✅ OK | neckband length incl. usable stretch ≥ head circumference |
| Measurements | Neckline (fabric edge) fits over the head | ≥ 50.0 cm | 57.8 cm | +78.1 mm | ✅ OK | neckline incl. stretch ≥ head circumference |
| Measurements | Sleeve length plausible | 31.9 cm – 44.4 cm | 43.7 cm | +0.0 mm | ✅ OK | arm length 35.5 cm |
| Measurements | Body length plausible | 29.4 cm – 60.8 cm | 38.2 cm | +0.0 mm | ✅ OK | from the neck point |
| Geometry | Front: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.0 cm; Neckline: 0.7 cm |
| Labels | Front: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Back: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.0 cm; Neckline: 0.7 cm |
| Labels | Back: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Raglan sleeve: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Sleeve hem: 2.0 cm; Neckline: 0.7 cm |
| Labels | Raglan sleeve: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Neckband: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 0.7 cm included |
| Labels | Neckband: grainline & cutting | present | cut 1 |  | ✅ OK | Rib knit |
| Geometry | Front: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Back: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Raglan sleeve: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Sleeve hem: corners mirrored at the fold line |
| Geometry | Front: cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.3° off 90° |  | ✅ OK | Centre (fold) |
| Geometry | Back: cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.5° off 90° |  | ✅ OK | Centre (fold) |
| Labels | Front: notches | on the cutting line | 1 notch mark(s) |  | ✅ OK |  |
| Labels | Back: notches | on the cutting line | 2 notch mark(s) |  | ✅ OK |  |
| Labels | Raglan sleeve: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |

**Result:** 32 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"chest_width": 594}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `chest_width` | 59.4 cm | chest × (1 + 8 % ease) |  |
| `neck_width_half` | 6.8 cm | neck / 5 + 1.5 cm |  |
| `front_neck_depth` | 8.3 cm | neck_width_half + 1.5 cm |  |
| `back_neck_depth` | 1.5 cm | fixed |  |
| `shoulder_length` | 8.5 cm | shoulder + allowance for fit 'normal' |  |
| `shoulder_slope` | 17 | fixed |  |
| `armhole_depth` | 13.2 cm | 18 % of chest_width + 2.5 cm |  |
| `body_length` | 38.2 cm | back length + 13 % of height |  |