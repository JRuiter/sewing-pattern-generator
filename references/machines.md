# Machines: what the sewist owns changes the pattern

Loaded when the user names their machines (SKILL.md step 2).

Pass them with `--machines sewing,overlocker,coverstitch` (keys: `sewing` = straight
stitch + zigzag, `straight_only`, `stretch_stitch`, `twin_needle`, `overlocker`, `coverstitch`;
German names such as Overlock, Coverlock, Zwillingsnadel work too; spec field `machines`). The
machines belong to the person who sews, so the first time they name them, save them once for all
future patterns: `python scripts/profiles.py machines set sewing,overlocker` (workshop file
`profiles/_machines.json`; a measurement profile may carry its own `--machines`, and `--machines`
wins over both). Effects: knit seams on the overlocker get 7.5 mm allowance (the knife trims),
woven seams on a straight-stitch-only machine 15 mm for French seams (an explicit
`--seam-allowance` always wins; doll clothes keep their 6 mm); every seam and hem step names the
machine and stitch; the instructions get a "Your machines" table (stitch, width/length, needle per
kind of step) and tips for what is missing (e.g. a twin needle instead of a coverstitch). Without
an overlocker nothing is missing: knit seams use a narrow zigzag/stretch stitch. A knit on a
straight-stitch-only machine works but is fragile: suggest a woven fabric or the double row of
long straight stitches the instructions describe. **No sewing machine at all** (only an
overlocker): `--machines overlocker,hand` (or `overlocker_only`; `hand` without any sewing-machine
key means "no sewing machine"). Then every seam is overlocked (7.5 mm allowance, woven fabric too)
and every straight-stitch step is done by hand: topstitching → back stitch, hems/casings → blind
stitch, basting → tacking stitch, bar tacks by hand, elastic ends → a box of hand stitches; the
steps add overlocker hints (pins out before the knife, curves slowly, thread chains).

The steps follow the machines the user owns (spec option `machines`, e.g.
`["sewing", "overlocker", "coverstitch"]`): overlocker seams, coverstitch hems, otherwise zigzag/twin needle.
Code: `scripts/machines.py` (`method(options, kind, knit)` / `tool_for` per step kind: seam, finish,
hem, topstitch, band).
