# Print specifications

Apply to every output of `scripts/render.py`. Checked automatically by
`tests/test_validate.py` (control square, embedded fonts, line widths, overlap).

## General

| Requirement | Implementation |
|---|---|
| Vector PDF, scale 1:1 | reportlab, units mm → pt (1 mm = 2.8346 pt), no raster graphics in the pattern |
| Fonts embedded | DejaVu Sans (TrueType, `assets/fonts/`, free license) |
| Line widths ≥ 0.5 pt | cutting line 1.0 pt, fold 1.0 pt, seam line 0.6 pt, markings 0.6–0.8 pt, tile frame 0.5 pt |
| Line styles | cutting line **solid**, seam line **dashed**, fold **dash-dot** |
| Control square | on every page/sheet: 5 × 5 cm (exactly 141.73 pt) + 1 inch (72 pt) |
| Labels per piece | name, size, "cut n" (mirrored pair/on fold), grainline arrow, notches (single/double), seam allowance note, "◄ PLACE ON FOLD ►" |
| Printing note | "Print at 100 % / "Actual size". Do NOT use "Fit to page"." in the header of every file |

## Roll (plotter)

- Page width = roll width − 10 mm (610 → 600 mm, 914 → 904 mm), variable length,
  **portrait** (the page is never wider than it is long).
- Margin 5 mm, header 80 mm (title, legend, control squares).
- Pieces are packed tightly: rotation in 15° steps is allowed (the grainline rotates with
  the piece), gap ≥ 10 mm, several strategies, the shortest length wins. No piece is cut.
- Exception: a piece wider than the roll (e.g. an adult circle skirt) is split into
  roll-wide strips of 120 cm with 10 mm overlap and glue marks; the sewing instructions
  point this out.

### Canon imagePROGRAF iPF650 (24" roll, 610 mm)
1. Open the PDF in **Adobe Acrobat** → Print → "Actual size", "Fit to page" OFF.
2. Paper size: **custom, 600 mm × page length** (shown in the file name/header),
   **portrait**. Do not let it rotate ("Auto-rotate" OFF).
3. Alternatively **imagePROGRAF Direct Print & Share**: roll paper, "Original size",
   borderless OFF.
4. After printing, measure the control square (5.0 × 5.0 cm).

## A0 / A1 (copy shop)

- Pieces whole, on as few sheets as possible (margin 10 mm), control square on each sheet.
- If a piece fits on no sheet, it is tiled like A4 (overlap + glue marks) and appended as
  its own section.

## A4 / US Letter to tape together

- Tiles with **10 mm overlap**; the glue area is shaded grey and identical on both pages
  (same content, tested automatically). On each page, trim the left or top margin along
  the dashed line and glue it onto the neighbouring page.
- Page label as row/column (A1, A2, B1 …), large in the background and in the header
  ("glue to left: A1, top: …").
- Registration marks: diamonds with the labels of both pages (e.g. "A1|A2") on every glue
  edge so that the pages match unambiguously.
- Margin 8 mm (printer margin); empty pages are left out.
- **Page 1 = overview:** reduced layout of all pages with labels, assembly instructions and
  printing note (the plan itself is scaled down, the control squares on it are 1:1).
- Control square on every page in a free spot (no pattern lines).

## Projector (`projector`, `projector_dark`)

For projector sewing (projecting the pattern straight onto the fabric):

- **One page at 1:1**, width `projector_width_mm` (default 1500 mm = a 150 cm fabric), height
  as needed (rounded up to 1 cm). No tiling.
- Pieces are packed with the **grainline parallel to the long page edge**, so the selvage
  can be laid along it.
- **Calibration grid** of 10 × 10 cm squares across the whole page (each square is exactly
  283.46 pt), labelled every 10 cm along the top and left edge, plus the 5 × 5 cm and
  1 inch control squares in the header. Adjust the projector until the squares measure
  exactly.
- **Thick lines:** cutting line 2 pt, all other lines ≥ 1 pt (dashes as on paper).
- `projector_dark`: black background, white cutting line, yellow seam line, cyan grainline,
  dark grey grid; easier to see on most fabrics in a darkened room.

## Additional files

- `*_master_1to1.svg`: SVG with unit mm (`width="…mm"`), 1:1, for plotter/CAD software.
- `*_preview.png`: coloured preview with page/strip grid.
- `*_aama.dxf` (format `dxf`) / `*_aama_14.dxf` (format `dxf14`): DXF R12 ASCII, unit mm,
  1:1, y up, readable by LibreCAD, Inkscape, cutter software and pattern CAD. Each piece is
  one BLOCK, inserted at its position from a 1600 mm wide layout. Layers follow the AAMA
  convention used in the apparel industry:

  | Layer | Content |
  |---|---|
  | 1 | cutting line (closed polyline incl. seam allowance) and piece texts (`Piece Name:`, `Size:`, `Quantity:`, `Material:`) |
  | 8 | seam line (`dxf`) and internal lines (pocket placement, fold-over lines) |
  | 14 | seam line (`dxf14`, for programs that expect it there) |
  | 6 | fold edges ("cut on fold" = mirror line) |
  | 4 | notches, one line per notch starting on the cutting line |
  | 7 | grainline |

  A 50 × 50 mm control square on layer 8 sits below the pieces. Umlauts in texts are
  transliterated (R12 is ASCII).
- `body_measurements.smis` (with `--export-measures`): the body measurements used, as an
  XML measurement file that pattern CAD programs can open; can be read back with
  `--measures-file`.
- `cutting_layout.png`: position of the pieces on the fabric (grainline parallel to the
  selvage) with fabric consumption. Layout modes (`--fabric-layout`, spec `fabric_layout`):
  - `single`: single layer, every copy placed separately, cut-on-fold pieces unfolded,
    mirrored copies flipped.
  - `folded`: fabric folded selvage to selvage (half width, double layer). Cut-on-fold pieces
    lie with their fold edge on the fabric fold; every other placement cuts a mirrored pair
    through both layers ("×2"). Pieces wider than the folded fabric go to a single-layer
    section after the folded part (noted in the instructions).
  - `auto` (default): from a fabric width of 130 cm both are computed and the shorter one is
    used (ties go to folded); narrower fabric (e.g. rib knit) is always single layer. The
    instructions name the mode and the length the other one would need.
