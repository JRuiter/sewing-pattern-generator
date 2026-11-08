# Doll clothes (`--doll`)

For a fabric doll, soft toy or fashion doll (height 20–100 cm). Size tables and proportions:
`references/size_tables.md` ("Doll clothes").

Ask for the doll's height (head to feet) and, measured with a tape or a string around the doll: chest,
waist, hip, head, arm length (shoulder to wrist), inseam and side length (waist to soles).
Only the height is required; missing values follow typical fabric-doll proportions. Then
`generate.py --doll --garment dress --measures '{"height": 45, "chest": 30, …}'`
(spec `"doll": true`). Supported: `dress`, `skirt`, `pants_basic`, `tshirt_basic`. Doll defaults
(each can be overridden): seam allowance 6 mm (5 mm under 30 cm), hems 10 mm, woven fabric, wide
fit, tops and dresses open completely at the back (Velcro/snaps, because a stuffed head rarely
fits through a neckline) with a bias-bound neckline, pants with a narrow elastic casing, no
pockets/cuffs. Recommend thin cotton, a short stitch and fray stop. A doll gets a profile with
`profiles.py save rosa --measures '{…}' --kind doll`. Details: `scripts/doll.py`,
`references/size_tables.md` ("Doll clothes").

## Copying doll clothes from a photo (mode B)
Doll clothes can be copied too: add `--doll` (`reverse.pipeline.run(..., doll=True)`); the
result has doll allowances and a back opening, and `generate.py --project` prints it. Doll tops
measure best with long sleeves (very short, wide doll sleeves: take the sleeve width with a tape).
