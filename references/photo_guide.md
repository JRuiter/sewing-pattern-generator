# Photo guide for users

Claude can pass these texts on to the user directly (shortened, in the user's language).

## Mode A: "I'd like something like this" (inspiration photo)

Any photo works: worn, catalogue, Pinterest, screenshot. From it I can tell **style and
proportions** (silhouette, length, pockets, cuffs, neckline, sleeve type, hood …) and show
you a feature list with how sure I am, for you to confirm.

What an inspiration photo does **not** give: exact measurements. For that I need the **size
or the body measurements** of the person you are sewing for. I will ask about the back and
hidden details instead of guessing. A designer pattern is not copied: you get an original
construction in a similar style for private use.

Helpful: front and back view, a close-up of pockets and cuffs, and the fabric
(e.g. "sweat, a little stretchy").

## Mode B: "Copy my favourite garment"

### You need
- the garment, washed and ironed or smoothed out,
- a **plain, high-contrast surface** (floor, table, bed sheet: light for a dark garment,
  dark for a light one),
- the **reference card** (`assets/reference-card.pdf`, printed at **100 %**; the square must
  measure 10.0 × 10.0 cm) **or** a folding ruler/tape measure,
- a smartphone camera.

### How to take the photo
1. Lay the garment **flat**, smooth out wrinkles, do not stretch it.
   - Pants: front side up, legs slightly spread so the crotch is visible.
   - Top: front side up, sleeves spread out sideways.
2. Lay the **reference card** flat next to it (not on the garment, not folded, all four
   corner markers visible). Without the card: lay a folding ruler along two edges.
3. Camera **straight from above**, whole garment + card in the picture, about 10 % margin.
   Standing on a chair helps. I can correct a slight tilt, but not a strong one.
4. Even light, no hard shadows, no flash.
5. One photo per side. For pants these also help:
   - **Crotch curve:** fold one leg inwards over the other so the front or back crotch seam
     lies flat; one photo each for front and back.
   - **Back** (for back pockets, back rise).
   For tops: one photo, front up, sleeves spread sideways and smoothed along their top
   fold; the neckline flat and visible (it shows me whether the sleeves are set in or
   raglan). Optional: fold the sleeve back so the **armhole** seam lies flat.

### Tape-measure values (take precedence)
If you like, measure as well and send me the values in cm:
waistband (relaxed, flat × 2), hip width, inseam, outseam, leg opening. For tops: the chest
width lying flat, about 2–3 cm below the armpit: I use it to correct the scale of the whole photo
(worth it for wide garments with long sleeves).
For cuffs: measure relaxed, not stretched.

### What happens next
1. I detect the card, rectify the photo (perspective) and work out the scale.
2. I separate the garment from the background and measure widths and lengths (lying flat =
   2 layers, so width = 2 × flat width).
3. You get an **overlay image** with the detected outline and all measurements to check. If
   something is wrong, just correct the value.
4. From that I reconstruct the pattern with the same drafting rules as always (smooth
   curves, right angles), check that the pattern gives your garment back exactly
   (tolerance: lengths ± 1 cm, widths ± 2 %), and show you the deviation report.
5. I save the result as a project (`project.json`) so that later you can say:
   "like the one from last time, but 2 sizes bigger".

### Common problems
| Message | Fix |
|---|---|
| "Reference card not found" | whole card in the picture, flat, not reflecting; printed at 100 %? |
| Outline frays / background detected too | higher-contrast surface, avoid shadows |
| Crotch detected wrongly | spread the legs a bit further, inner leg edges visible |
| Measurements look too big/small | measure the control square on the card; was the garment stretched? |

### Doll clothes
Doll clothes can be copied the same way (`--doll`): lay them flat next to the card (the card
may be bigger than the garment, that is fine) and photograph them from closer up. The result
gets doll allowances (6 mm) and, for tops, a back opening. Doll pants are measured fully
automatically, even with very short, wide legs. For doll tops lay the sleeves out straight;
very short, wide sleeves are hard to read from the photo, so measure their width flat with a
tape (`tape={"bicep_flat": 5.5, "opening_flat": 5.5}`, cm). Doll clothes have no sizes, so
"two sizes bigger" does not apply: measure the new doll and use the doll mode instead.

### Limits
- Mode B is fully automatic for **pants** (widths, rise, inseam, outseam, waistband,
  cuffs) and for **T-shirts with set-in or raglan sleeves** (chest, hem, length, underarm,
  neckline, shoulder, upper arm, sleeve length and opening). Hoods, collars and cuffs on tops
  are not copied yet.
- With long sleeves spread out the garment is very wide compared to the card: hold the camera
  really level, or give me the chest width from the tape measure.
- Style lines, zips and collars are recognised but not drafted; I tell you openly what is
  left out.
