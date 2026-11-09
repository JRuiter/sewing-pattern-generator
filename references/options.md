# generate.py options

Everything `scripts/generate.py` accepts besides garment, size and format (CLI flags; the spec JSON
uses the same names, see the header of `generate.py`).

## Sizes, nested sizes, units, language
Sizes: kids as a number (`122`), women as `w38`, men as `m52`; US/UK: `us8` (US women's),
`uk12` (UK women's), `us3t` (US toddler), `usk8` (US kids), see `references/size_tables.md`.
**Several sizes at once (nested):** `--size 98,110,122` (or a range `98-122` in kids' steps)
drafts and validates every size and overlays them at a shared construction point, each size in
its own colour/line, PDF layer (switch sizes on/off in Acrobat's *Layers* panel) and SVG group.
Use it for siblings or to blend between sizes; all sizes share the same options.
Imperial users: `--units imperial` (measurements in inches, reports in inches/yards).

**German output:** `--lang de` (spec `"language": "de"`) writes every output in German: piece labels, sewing
steps, booklet, cutting layout, reports and diagrams, with German file names (`naehanleitung.pdf`,
`pruefbericht.md`, `zuschnittplan.png`, `schnitt.json`, `…_master_1zu1.svg`, `…_a4_kleben.pdf`), decimal
commas and "Gr. 122". All texts go through one string table (`scripts/i18n.py`, German entries in
`scripts/i18n_de.py`); a new output text needs a German entry there. Option names and construction value keys stay English.

## Modules and options

| Module | Styles/options |
|---|---|
| `pants_basic` | style: jogger, harem, leggings, trousers · fit · fabric · stretch · length (long, 7/8, knee, short) · waistband (casing, rib, yoga, tunnel) · cuffs · pockets ([side] = slanted front pocket with pocket bag, [back_patch], [cargo]) · leg_shape (straight, tapered, bootcut, flare + flare_cm; long legs without cuffs) · turn_up (cm, shorts/knee length) · fake_fly (true or {offset_mm, length_frac_R, radius_mm, side}) · back_pockets (1, 2) + back_pocket_side (right, left; as worn) · hem_finish (plain, elastic_casing + hem_elastic_mm, hem_elastic_len_cm) · pocket_bag_fabric (cotton, jersey, lining, main) |
| `tshirt_basic` | fit · fabric · sleeve_style (set_in, raglan) · sleeve_length (short, 3/4, long) · neckline (round, v) · length (normal, tunic) · sleeve_cuffs · hem_band |
| `hoodie` | like the T-shirt + hood, hood_lining, kangaroo (default: sweat, wide, rib cuffs) · front (closed, zip: zip-up jacket with split front, side pockets, zip guard, zip length in the notes) · zip_guard |
| `skirt` | style: gathered, a_line, circle · length (mini, knee, midi, maxi) · gather · flare_deg |
| `dress` | style: waist_seam (T-shirt bodice + skirt: gathered, a_line, circle; gather 1.0–2.5; waist_elastic; pockets in the side seam), shirt_dress (A-line T-shirt dress, flare_cm) · length (mini, knee, midi, maxi) · all T-shirt sleeve/neckline options |
| `beanie` | brim, slouch |
| `loop` | wraps (1 = single, 2 = worn doubled), height |
| `jeans` | five-pocket jeans with zip fly, scoop pockets, back yoke · fit · leg_shape (straight, tapered, bootcut, flare) · length · coin_pocket · belt_loops · back_pockets (0–2) |
| `dungarees` | style (trousers, jogger, short) · bib_pocket · length · cuffs · pockets · woven or sweat |
| `shirt` | style: shirt (yoke, shirt collar, cuffs, chest pocket), blouse (bust dart) · fit · sleeve_length (short, long) · collar (shirt, stand, peter_pan, none = bias-bound neckline) · yoke · bust_dart · pocket · cuffs · buttons |
| `polo` | fit · sleeve_length · sleeve_cuffs · collar_fabric (rib, main) · side_vents · buttons |
| `cardigan` | neckline (v, round) · sleeve_length · sleeve_cuffs · hem_band · band_fabric (main, rib) · pockets · buttons |
| `vest` | closure (zip, snaps, none) · collar · pockets · binding_fabric · fleece, sweat or woven |
| `jacket` | style (jacket, coat) · collar (stand, none) · pockets (welt, jetted, flap) · lining · buttons · length (hip, thigh, knee) |
| `coat` | the lined jacket at knee length (length: hip, thigh, knee), flap pockets |
| `softshell` | hood · pockets (zip pockets) · cuff_tabs · hem_drawcord |
| `fitted_dress` | woven fitted bodice with darts and invisible zip · skirt (a_line, gathered, circle) · length · sleeve_length (short, long, none) · neckline · pockets |
| `wrap` | style (top, dress) · sleeve_length · length (dress) · overlap |
| `pinafore` | skirt (gathered, a_line) · length · gather · pockets |
| `bodysuit` | style: body (snap crotch), swimsuit (lined front, elastic edges, swim fabric), wrap (baby kimono body) · sleeve_length (short, long, none) · leg_cut (normal, high) |
| `underwear` | style: briefs (burrito gusset, elastic edges), boxers (boxer briefs) · leg_cut (normal, high, low) · rise (mid, low) · leg_length (cm, boxers) |
| `swim_trunks` | liner (mesh brief, default true) · length (short, knee) · pockets (mesh pocket bags) · fit |
| `jumpsuit` | style: jumpsuit, boiler · length (long, 7/8, short = playsuit) · sleeve_length · closure (buttons, zip) · collar (none, stand, shirt) · pockets · belt · chest_pocket |
| `pyjama` | top (tshirt, shirt) · length (long, short = shorty) · cuffs · collar (shirt top); top and pants in one booklet and layout |
| `romper` | baby sizes 50–92 (write `b50`/`b56` for the smallest) · sleeve_length (long, short) · feet (sole instead of rib cuffs); snaps along the inner legs |
| `sleeping_bag` | style: sleeping_bag (two-way zip), swaddle (newborns 50–68, wrap wings with Velcro) · tog (0.5 summer, 1.0 all year, 2.5 winter: jersey lining, + thin or thick wadding) |
| `scarf` | style (tube, flat) · length_cm · width_cm · fringe |
| `headband` | style (plain, twist) · height_cm |
| `neckwear` | style (gaiter, neckerchief) · height_cm |
| `bib` | style (classic, bandana) · absorbent · length_cm |
| `mittens` | thumb · cuff · cuff_cm · string |
| `gloves` | style (outline) · cuff_cm · finger_lengths_cm |
| `socks` | style (profile, sole) · length (ankle, crew, knee) · cuff |
| `earflap_hat` | ties · flap_cm |
| `bucket_hat` | reversible · brim_cm · band_cm · brim_slope |
| `cap` | peak_cm · ease_cm |
| `bag` | style (tote, drawstring) · bag_size (small, medium, large) or width_cm/height_cm/depth_cm · pocket · handle_cm · lining |

**Style lines** (`style_lines`, modules `tshirt_basic`, `hoodie`, `dress`, `sweater`): `princess` (armhole
princess seams front and back), `yoke` (front and back yoke), `color_block` (body split across the chest,
upper part in a contrast fabric). The fit stays the same; the panels can be cut from different fabrics.

Fabrics: woven, corduroy, velvet, jersey, jersey_elastane, interlock, sweat, fleece, rib, softshell,
swim_woven (quick-dry swim fabric), swim_lycra (swimsuit fabric). Extra fabric groups in the cutting layout:
mesh (swim liner, pocket bags), wadding (sleeping bag), contrast fabric (colour blocking), lining. Corduroy and
velvet have a nap (option `nap`, also `nap: true` for any other fabric): every main-fabric piece is
cut with the top towards the same fabric end, and the pressing note says to press from the wrong side.
Print of the main fabric (all modules): `fabric_print` plain (default), one_way (directional print,
cut like a nap), stripes or plaid with `print_repeat_cm` (number, or `[across, along]` for checks);
CLI `--fabric-print`, `--print-repeat 4` or `--print-repeat 6,8`. Stripes and checks are matched at
the seams in the cutting layout (see `references/print_specs.md`).
All modules: `title` (e.g. "Kordhose") replaces the garment name on the pieces, in the instructions and
in the file names.
Fits: slim, normal, wide, oversized, boxy (tops: wide and straight, dropped shoulder, low cap, slightly cropped, hem band barely drawn in), harem.

Seam allowance (all modules): `--seam-allowance 7.5` (mm, all seams), `--hem-allowance 30`
(turned-up hems), `--seam-allowance none` (pattern without allowances: only the seam line is
drawn and every piece lists what to add). Spec options: `seam_allowance_mm`,
`hem_allowance_mm`, `seam_allowance: "none"`. Fold edges stay at 0; casings, facings and the
narrow circle-skirt hem keep their construction allowance.

Formats: `rollNNN` (page width = roll − 10 mm, portrait; pieces wider than the roll are
split automatically into strips with glue marks), `a0`, `a1` (pieces whole, oversized
pieces tiled), `a4`, `letter` (tiles with 10 mm overlap and an overview page), `dxf` /
`dxf14` (DXF for cutting machines and CAD, AAMA layers, see `references/print_specs.md`),
`projector` / `projector_dark` (one page 1:1 for projector sewing, 10 cm calibration grid,
thick lines).
Always written as well: SVG master 1:1, PNG preview, cutting layout PNG, sewing
instructions (PDF: illustrated booklet: title page with the finished garment from the front and the back
(`views.py`: legs, bands, cuffs, sleeves, hood from the real pieces), size/fabric, parts, steps, difficulty
and what it is sewn with; parts at one scale with count badges, seam allowances, material in two columns
(fabric amounts, notions, machines, tools) and the colour/line legend; the basics for the machines in use
(overlocker, hand stitches, sewing machine), each in a box; the steps two per page, each with its picture from the real pieces, 2–4 numbered actions and
the yellow "Important" / green "Tip" boxes (`Step.tip` / `Step.hint`); 1:1 templates for lines transferred
after cutting (`Mark.template`) after the "Done!" panel; plus Markdown with a PNG per step in `steps/`), `pattern.json`,
`validation_report.md`. The steps follow the machines the user owns (spec option `machines`, e.g.
`["sewing", "overlocker", "coverstitch"]`): overlocker seams, coverstitch hems, otherwise zigzag/twin needle.
Cutting layout: `--fabric-layout auto|folded|single` (default `auto` = the shorter of
folded selvage to selvage and single layer; see `references/print_specs.md`).

## Fine tuning and toile feedback

Fine tuning: the report lists the **construction values** (hip width, crotch extensions,
rise, armhole depth, …) with how they were derived. To change one, e.g. after a toile
("seat too tight" → larger `back_crotch_extension`), pass
`--construction '{"back_crotch_extension": 95}'` (mm) and generate again; validation
still checks the result. Notch shape: `--notch-style slit|t|v` (v for cutting machines and
projector use).

**Toile feedback:** after delivery, offer once: "Tell me how the test garment fits (e.g. 'hip
2 cm too tight, crotch 1.5 cm too low') and I'll adjust the pattern." Then
`--adjust '{"hip_tight": "2cm", "crotch_low": "1.5cm"}'` (or signed changes such as
`{"hip": "+2cm", "sleeve_length": "-3cm"}`; spec field `adjustments`). The instructions show
before/after finished measurements; the adjustments stay in `pattern.json`/`project.json`
and are re-applied in other sizes. Keys: `references/drafting_rules.md` §8.
