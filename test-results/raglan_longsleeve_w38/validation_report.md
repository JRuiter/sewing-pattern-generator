### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 43.4 cm | 43.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam front: front ↔ sleeve | 23.0 cm | 23.0 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam back: back ↔ sleeve | 26.5 cm | 26.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Sleeve seam (front ↔ back) | 53.0 cm | 52.9 cm | -1.2 mm | ✅ OK |  |
| Seam pairs | Neckband ↔ neckline (stretched) | 70–85 % of 52.6 cm | 36.8 cm = 70 % | -157.9 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Underarm: side seam ↔ raglan (body) | 90° | 90.4° | +0.4° | ✅ OK |  |
| Angles/transitions | Underarm: sleeve seam ↔ raglan (sleeve front) | 90° | 89.7° | -0.3° | ✅ OK |  |
| Angles/transitions | Neckline at centre front | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Neckline at centre back | 90° | 89.6° | -0.4° | ✅ OK |  |
| Angles/transitions | Hem at centre front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | -0.0° | ✅ OK |  |
| Measurements | Chest circumference pattern = body + ease | 95.0 cm | 95.1 cm | +0.0 % | ✅ OK | body 88.0 cm + +8 % ease |
| Measurements | Neckline fits over the head | ≥ 55.2 cm | 66.3 cm | +110.6 mm | ✅ OK | neckband length incl. usable stretch ≥ head circumference |
| Measurements | Neckline (fabric edge) fits over the head | ≥ 55.2 cm | 73.7 cm | +184.3 mm | ✅ OK | neckline incl. stretch ≥ head circumference |
| Measurements | Sleeve length plausible | 53.5 cm – 74.4 cm | 71.1 cm | +0.0 mm | ✅ OK | arm length 59.5 cm |
| Measurements | Body length plausible | 50.4 cm – 104.2 cm | 63.0 cm | +0.0 mm | ✅ OK | from the neck point |
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
| Geometry | Front: cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.2° off 90° |  | ✅ OK | Centre (fold) |
| Geometry | Back: cut-on-fold edge | straight, no SA, 90° corners, on grain | ok, corners ≤ 0.4° off 90° |  | ✅ OK | Centre (fold) |
| Labels | Front: notches | on the cutting line | 1 notch mark(s) |  | ✅ OK |  |
| Labels | Back: notches | on the cutting line | 2 notch mark(s) |  | ✅ OK |  |
| Labels | Raglan sleeve: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |

**Result:** 32 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"chest_width": 950}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `chest_width` | 95.0 cm | chest × (1 + 8 % ease) |  |
| `neck_width_half` | 8.5 cm | neck / 5 + 1.5 cm |  |
| `front_neck_depth` | 11.0 cm | neck_width_half + 2.5 cm |  |
| `back_neck_depth` | 2.0 cm | fixed |  |
| `shoulder_length` | 12.5 cm | shoulder + allowance for fit 'normal' |  |
| `shoulder_slope` | 17 | fixed |  |
| `armhole_depth` | 19.6 cm | 18 % of chest_width + 2.5 cm |  |
| `body_length` | 63.0 cm | back length + 13 % of height |  |