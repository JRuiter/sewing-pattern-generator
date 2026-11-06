### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 36.3 cm | 36.3 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam front: front ↔ sleeve | 17.5 cm | 17.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Raglan seam back: back ↔ sleeve | 20.6 cm | 20.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Sleeve seam (front ↔ back) | 52.3 cm | 52.2 cm | -1.6 mm | ✅ OK |  |
| Seam pairs | Neckband ↔ neckline (stretched) | 70–85 % of 46.2 cm | 32.4 cm = 70 % | -138.7 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Underarm: side seam ↔ raglan (body) | 90° | 90.6° | +0.6° | ✅ OK |  |
| Angles/transitions | Underarm: sleeve seam ↔ raglan (sleeve front) | 90° | 89.7° | -0.3° | ✅ OK |  |
| Angles/transitions | Neckline at centre front | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Neckline at centre back | 90° | 89.6° | -0.4° | ✅ OK |  |
| Angles/transitions | Hem at centre front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | -0.0° | ✅ OK |  |
| Measurements | Chest circumference pattern = body + ease | 74.5 cm | 74.6 cm | +0.1 % | ✅ OK | body 69.0 cm + +8 % ease |
| Measurements | Neckline fits over the head | ≥ 53.5 cm | 58.2 cm | +47.4 mm | ✅ OK | neckband length incl. usable stretch ≥ head circumference |
| Measurements | Neckline (fabric edge) fits over the head | ≥ 53.5 cm | 64.7 cm | +112.1 mm | ✅ OK | neckline incl. stretch ≥ head circumference |
| Measurements | Sleeve length plausible | 50.4 cm – 70.0 cm | 66.5 cm | +0.0 mm | ✅ OK | arm length 56.0 cm |
| Measurements | Body length plausible | 42.0 cm – 86.8 cm | 52.2 cm | +0.0 mm | ✅ OK | from the neck point |
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
| Labels | Front: notches | on the cutting line | 1 notch mark(s) |  | ✅ OK |  |
| Labels | Back: notches | on the cutting line | 2 notch mark(s) |  | ✅ OK |  |
| Labels | Raglan sleeve: notches | on the cutting line | 3 notch mark(s) |  | ✅ OK |  |

**Result:** 30 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"chest_width": 745}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `chest_width` | 74.5 cm | chest × (1 + 8 % ease) |  |
| `neck_width_half` | 7.7 cm | neck / 5 + 1.5 cm |  |
| `front_neck_depth` | 9.2 cm | neck_width_half + 1.5 cm |  |
| `back_neck_depth` | 1.5 cm | fixed |  |
| `shoulder_length` | 11.2 cm | shoulder + allowance for fit 'normal' |  |
| `armhole_depth` | 15.9 cm | 18 % of chest_width + 2.5 cm |  |
| `body_length` | 52.2 cm | back length + 13 % of height |  |