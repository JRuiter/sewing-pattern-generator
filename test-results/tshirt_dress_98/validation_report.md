### Sewability check

| Area | Check | Target | Actual | Δ | Result | Note |
|---|---|---|---|---|---|---|
| Seam pairs | Side seam front ↔ back | 41.6 cm | 41.6 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Armhole ↔ sleeve cap (ease) | ease 0–5 mm | 26.4 cm ↔ 26.6 cm | +2.0 mm | ✅ OK | Jersey: 0–5 mm |
| Seam pairs | Shoulder seam front ↔ back | 8.5 cm | 8.5 cm | +0.0 mm | ✅ OK |  |
| Seam pairs | Sleeve seam (front ↔ back) | 3.7 cm | 3.7 cm | -0.0 mm | ✅ OK |  |
| Seam pairs | Neckband ↔ neckline (stretched) | 70–85 % of 40.4 cm | 28.2 cm = 70 % | -121.1 mm | ✅ OK | rib band is stretched while sewing |
| Angles/transitions | Underarm: side seam ↔ armhole front | 90° | 90.5° | +0.5° | ✅ OK |  |
| Angles/transitions | Underarm: side seam ↔ armhole back | 90° | 90.7° | +0.7° | ✅ OK |  |
| Angles/transitions | Shoulder ↔ armhole (front + back) | 180° | 179.4° | -0.6° | ✅ OK |  |
| Angles/transitions | Sleeve cap top (smooth) | 180° | 177.9° | -2.1° | ✅ OK |  |
| Angles/transitions | Sleeve underarm ↔ cap front | 90° | 89.2° | -0.8° | ✅ OK |  |
| Angles/transitions | Shoulder ↔ neckline (front + back) | 180° | 180.4° | +0.4° | ✅ OK |  |
| Angles/transitions | Neckline at centre front | 90° | 90.3° | +0.3° | ✅ OK |  |
| Angles/transitions | Neckline at centre back | 90° | 89.5° | -0.5° | ✅ OK |  |
| Angles/transitions | Hem at centre front | 90° | 90.0° | +0.0° | ✅ OK |  |
| Angles/transitions | Hem ↔ side seam front | 90° | 90.0° | -0.0° | ✅ OK |  |
| Measurements | Chest circumference pattern = body + ease | 59.4 cm | 59.4 cm | +0.0 % | ✅ OK | body 55.0 cm + +8 % ease |
| Measurements | Neckline fits over the head | ≥ 50.0 cm | 50.8 cm | +8.5 mm | ✅ OK | neckband length incl. usable stretch ≥ head circumference |
| Measurements | Neckline (fabric edge) fits over the head | ≥ 50.0 cm | 56.5 cm | +65.0 mm | ✅ OK | neckline incl. stretch ≥ head circumference |
| Measurements | Dress fits over the hip | ≥ 59.3 cm | 66.6 cm | +73.0 mm | ✅ OK | width at hip level ≥ hip + 4 % |
| Measurements | Dress length plausible | 39.2 cm – 88.2 cm | 54.8 cm | +0.0 mm | ✅ OK | from the neck point |
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

**Result:** 34 OK, 0 warning(s), 0 error(s): the pattern is sewable.

### Construction values

Override any of these with the option `construction`, values in mm (e.g. `{"construction": {"chest_width": 594}}`).

| Name | Value | Derived from | Note |
|---|---|---|---|
| `chest_width` | 59.4 cm | chest × (1 + 8 % ease) |  |
| `neck_width_half` | 6.8 cm | neck / 5 + 1.5 cm |  |
| `front_neck_depth` | 8.3 cm | neck_width_half + 1.5 cm |  |
| `back_neck_depth` | 1.5 cm | fixed |  |
| `shoulder_length` | 8.5 cm | shoulder + allowance for fit 'normal' |  |
| `armhole_depth` | 13.2 cm | 18 % of chest_width + 2.5 cm |  |
| `body_length` | 54.6 cm | option body_length |  |