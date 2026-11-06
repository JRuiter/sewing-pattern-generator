### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 43.4 cm | 43.4 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Armhole ↔ sleeve cap (ease) | ease 0–5 mm | 40.0 cm ↔ 40.2 cm | +2.0 mm | ✅ OK | Jersey: 0–5 mm |
| Seam pairs | Shoulder seam front ↔ back | 12.5 cm | 12.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Sleeve seam (front ↔ back) | 6.2 cm | 6.2 cm | -0.0 mm | ✅ OK |  |
| Seam pairs | Neckband ↔ neckline (stretched) | 70–85 % of 51.4 cm | 36.0 cm = 70 % | -154.3 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Underarm: side seam ↔ armhole front | 90° | 90.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Underarm: side seam ↔ armhole back | 90° | 90.5° | +0.5° | ✅ OK |  |
| Angles/transitions | Shoulder ↔ armhole (front + back) | 180° | 179.9° | -0.1° | ✅ OK |  |
| Angles/transitions | Sleeve cap top (smooth) | 180° | 179.0° | -1.0° | ✅ OK |  |
| Angles/transitions | Sleeve underarm ↔ cap front | 90° | 89.4° | -0.6° | ✅ OK |  |
| Angles/transitions | Shoulder ↔ neckline (front + back) | 180° | 180.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Neckline at centre front | 90° | 90.2° | +0.2° | ✅ OK |  |
| Angles/transitions | Neckline at centre back | 90° | 89.6° | -0.4° | ✅ OK |  |
| Angles/transitions | Hem at centre front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | -0.0° | ✅ OK |  |
| Measurements | Chest circumference pattern = body + ease | 95.0 cm | 95.1 cm | +0.0 % | ✅ OK | body 88.0 cm + +8 % ease |
| Measurements | Neckline fits over the head | ≥ 55.2 cm | 64.8 cm | +95.5 mm | ✅ OK | neckband length incl. usable stretch ≥ head circumference |
| Measurements | Neckline (fabric edge) fits over the head | ≥ 55.2 cm | 72.0 cm | +167.5 mm | ✅ OK | neckline incl. stretch ≥ head circumference |
| Measurements | Body length plausible | 50.4 cm – 104.2 cm | 63.0 cm | +0.0 mm | ✅ OK | from the neck point |
| Geometry | Front: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.0 cm; Neckline: 0.7 cm |
| Labels | Front: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Back: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Hem: 2.0 cm; Neckline: 0.7 cm |
| Labels | Back: grainline & cutting | present | cut 1 on fold |  | ✅ OK | Main fabric |
| Geometry | Sleeve: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 1.0 cm included; Sleeve hem: 2.0 cm |
| Labels | Sleeve: grainline & cutting | present | cut 2 (mirrored pair) |  | ✅ OK | Main fabric |
| Geometry | Neckband: outline & seam allowance | closed, SA present | ok |  | ✅ OK | seam allowance 0.7 cm included |
| Labels | Neckband: grainline & cutting | present | cut 1 |  | ✅ OK | Rib knit |
| Geometry | Front: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Back: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Hem: corners mirrored at the fold line |
| Geometry | Sleeve: turned allowance lies flat | ≤ 0.5 mm | 0.0 mm |  | ✅ OK | Sleeve hem: corners mirrored at the fold line |
| Labels | Front: notches | on the cutting line | 1 notch mark(s) |  | ✅ OK |  |
| Labels | Back: notches | on the cutting line | 2 notch mark(s) |  | ✅ OK |  |
| Labels | Sleeve: notches | on the cutting line | 4 notch mark(s) |  | ✅ OK | 1 at corners |

**Result:** 33 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"chest_width": 950}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `chest_width` | 95.0 cm | chest × (1 + 8 % ease) |  |
| `neck_width_half` | 8.5 cm | neck / 5 + 1.5 cm |  |
| `front_neck_depth` | 11.0 cm | neck_width_half + 2.5 cm |  |
| `back_neck_depth` | 2.0 cm | fixed |  |
| `shoulder_length` | 12.5 cm | shoulder + allowance for fit 'normal' |  |
| `armhole_depth` | 19.6 cm | 18 % of chest_width + 2.5 cm |  |
| `body_length` | 63.0 cm | back length + 13 % of height |  |