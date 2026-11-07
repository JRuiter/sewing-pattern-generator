#!/usr/bin/env python3
"""Regenerate examples/ and test-results/ from the current code.

  python tools/make_examples.py            # both
  python tools/make_examples.py examples   # only examples/
  python tools/make_examples.py results    # only test-results/
  python tools/make_examples.py doll       # only examples/4_doll_dress_45cm_a4
  python tools/make_examples.py images     # only docs/images/ and the example READMEs (from examples/)
"""
from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import generate as GN  # noqa: E402
import measurements as M  # noqa: E402
import photo_synth as PS  # noqa: E402
from garments import get  # noqa: E402
from garments import pants_basic as PB  # noqa: E402
from reverse import pipeline as P  # noqa: E402
from reverse import verify as VF  # noqa: E402

VARIANTS = [
    ("harem_pants", "pants_basic", {"style": "harem", "fabric": "sweat"}),
    ("joggers", "pants_basic", {"style": "jogger"}),
    ("leggings", "pants_basic", {"style": "leggings"}),
    ("pull_on_trousers", "pants_basic", {"style": "trousers"}),
    ("tshirt", "tshirt_basic", {}),
    ("raglan_longsleeve", "tshirt_basic", {"sleeve_style": "raglan", "sleeve_length": "long"}),
    ("hoodie", "hoodie", {}),
    ("gathered_skirt", "skirt", {"style": "gathered"}),
    ("a_line_skirt", "skirt", {"style": "a_line"}),
    ("circle_skirt", "skirt", {"style": "circle"}),
    ("dress_gathered", "dress", {"style": "waist_seam", "skirt": "gathered", "pockets": True}),
    ("tshirt_dress", "dress", {"style": "shirt_dress"}),
    ("beanie", "beanie", {}),
    ("loop", "loop", {}),
]
SIZES = [(98, "98"), (140, "140"), ("w38", "women's 38")]


def _reset(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def make_results():
    out = os.path.join(ROOT, "test-results")
    _reset(out)
    rows = ["# Test results: sewability check", "",
            "Every garment in three sizes (kids 98, kids 140, women's 38), layout roll 610 mm.",
            "Each folder holds `validation_report.md` (the full check table) and a preview PNG.", "",
            "| Garment | Size | Checks | ✅ OK | ⚠️ Warning | ❌ Error | Preview |",
            "|---|---|---|---|---|---|---|"]
    tot = [0, 0, 0, 0]
    for name, garment, opts in VARIANTS:
        for size, label in SIZES:
            sub = f"{name}_{size}"
            d = os.path.join(out, sub)
            res = GN.run(dict(garment=garment, size=size, options=opts, formats=["roll610"], out=d,
                              basename=sub), verbose=False)
            keep = {"validation_report.md", f"{sub}_roll610_preview.png"}
            for f in os.listdir(d):
                if f not in keep:
                    fp = os.path.join(d, f)
                    shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
            rep = res["report"]
            n = [len(rep), sum(c.status == "OK" for c in rep), sum(c.status == "WARNING" for c in rep),
                 sum(c.status == "ERROR" for c in rep)]
            tot = [a + b for a, b in zip(tot, n)]
            rows.append(f"| {name.replace('_', ' ')} | {label} | {n[0]} | {n[1]} | {n[2]} | {n[3]} | "
                        f"[image]({sub}/{sub}_roll610_preview.png) |")
            print(sub, n)
    rows += ["", f"**Total:** {tot[0]} checks, {tot[1]} OK, {tot[2]} warnings, {tot[3]} errors."]
    with open(os.path.join(out, "OVERVIEW.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")


def make_examples():
    ex = os.path.join(ROOT, "examples")
    _reset(ex)
    harem = dict(garment="pants_basic", size=122, options={"style": "harem", "fabric": "sweat"})
    GN.run(dict(harem, formats=["roll610"], out=os.path.join(ex, "1_harem_pants_122_roll610")), verbose=False)
    GN.run(dict(harem, formats=["a4"], out=os.path.join(ex, "2_harem_pants_122_a4")), verbose=False)

    # 3: photo mode B round trip: joggers 116 → synthetic photo → reverse engineering → pattern
    d = os.path.join(ex, "3_photo_mode_b")
    os.makedirs(d)
    pat = PB.draft(M.size_measures(116), {"style": "jogger", "pockets": []})
    photo = os.path.join(d, "photo_flat_with_reference_card.jpg")
    _, truth = PS.synth_pants_photo(pat, photo, seed=3)
    with open(os.path.join(d, "truth_finished_mm.json"), "w", encoding="utf-8") as f:
        json.dump({k: round(float(v), 1) for k, v in truth.items()}, f, indent=1)
    res = P.run(photo, "pants", os.path.join(d, "project"))
    GN.run(dict(project=os.path.join(d, "project", "project.json"), formats=["roll610", "a4"],
                out=os.path.join(d, "pattern"), basename="joggers_copied"), verbose=False)
    keys = ["hip_circ", "thigh_circ", "knee_circ", "opening", "waist_relaxed", "outseam", "inseam", "front_rise"]
    rows = VF.compare(res["pattern"], truth, keys)
    labels = get("pants_basic").FINISHED_LABELS
    md = ["# Round-trip comparison: original pattern ↔ reconstruction from the photo", "",
          "The photo was generated synthetically from joggers size 116 (no pockets): sewn together "
          "virtually, laid flat, with the reference card, perspective, rotation, blur, noise and JPEG "
          "compression.", "",
          "| Measurement | Original (truth) | Reconstructed | Δ | Tolerance | Result |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        w = r["type"] == "width"
        d_txt = f"{r['delta'] / 10:+.1f} cm" + (f" ({r['rel'] * 100:+.1f} %)" if w else "")
        md.append(f"| {labels.get(r['key'], (r['key'],))[0]} | {r['target'] / 10:.1f} cm | "
                  f"{r['actual'] / 10:.1f} cm | {d_txt} | {'± 2 %' if w else '± 1 cm'} | "
                  f"{'✅' if r['ok'] else '❌'} |")
    md += ["", f"Detected fit: **{res['fit']['fit']}**, estimated size ≈ {res['fit']['size']}.", ""]
    with open(os.path.join(d, "round_trip_comparison.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\n".join(md))
    make_doll_example()

    # 5: hoodie with kangaroo pocket, size 140, A4 tiles: the booklet with the most steps
    GN.run(dict(garment="hoodie", size=140, options={"kangaroo": True}, formats=["a4"],
                out=os.path.join(ex, "5_hoodie_140_a4"), basename="hoodie_size140"), verbose=False)
    # 6: nested sizes: joggers 98/110/122 on one 610 mm roll, one colour and PDF layer per size
    GN.run(dict(garment="pants_basic", size="98,110,122", options={"style": "jogger"},
                formats=["roll610"], out=os.path.join(ex, "6_joggers_nested_98_110_122_roll610"),
                basename="joggers_98_110_122"), verbose=False)
    make_images()
    make_readmes()


# One README.md per example folder: the prompt, pictures, key facts and what every file is.
EXAMPLES = [
    ("1_harem_pants_122_roll610", "Harem pants, size 122, on a 610 mm roll",
     "Harem pants for my daughter, size 122, sweat fabric, print on the 24\" roll.",
     "Wide harem pants with an elastic waistband and rib cuffs, printed on one long page of a "
     "24\" (610 mm) plotter roll."),
    ("2_harem_pants_122_a4", "Harem pants, size 122, as A4 pages",
     "The same harem pants, but as A4 pages I can print at home.",
     "The same pattern as example 1, tiled onto A4 pages with 10 mm overlap, glue areas, row and "
     "column labels and an overview page."),
    ("4_doll_dress_45cm_a4", "Doll dress for a 45 cm fabric doll",
     "A dress for my daughter's 45 cm fabric doll. Chest 30 cm, waist 28 cm, hip 31 cm, head 32 cm.",
     "A gathered dress drafted from the doll's own measurements: 6 mm seam allowances, a back "
     "opening with Velcro instead of a neckline the head wouldn't fit through, bias-bound neckline."),
    ("5_hoodie_140_a4", "Hoodie with kangaroo pocket, size 140",
     "A hoodie with kangaroo pocket for my son, size 140, sweat fabric, A4 pages.",
     "Hood, kangaroo pocket, set-in sleeves, rib cuffs and hem band. The sewing booklet has the "
     "most steps of all examples."),
    ("6_joggers_nested_98_110_122_roll610", "Joggers in sizes 98, 110 and 122 on one sheet",
     "Joggers in sizes 98, 110 and 122 on one pattern, for the 24\" roll.",
     "Three sizes nested on one roll page. Each size has its own colour, line style and PDF layer "
     "(switch sizes off before printing), and every size is checked on its own."),
]


def _file_rows(d, rel=""):
    desc = [("_roll610.pdf", "Print file for the 610 mm roll, 1:1"),
            ("_tiled.pdf", "Print file as A4 pages to tape together (last page: overview)"),
            ("_master_1to1.svg", "The whole pattern as one 1:1 SVG"),
            ("_preview.png", "Preview picture of the print file"),
            ("cutting_layout.png", "Cutting layout on the fabric, with fabric amounts"),
            ("sewing_instructions.pdf", "Illustrated sewing booklet, then measurements, pieces and checks"),
            ("sewing_instructions.md", "The same instructions as text, with a picture per step"),
            ("validation_report.md", "Every sewability check with target and actual value"),
            ("pattern.json", "All pieces, measurements and construction values as data"),
            ("steps", "Step pictures used by sewing_instructions.md")]
    rows = []
    for f in sorted(os.listdir(d)):
        for suffix, text in desc:
            if f.endswith(suffix):
                rows.append(f"| [`{rel}{f}`]({rel}{f}) | {text} |")
                break
    return ["| File | What it is |", "|---|---|"] + rows


def _facts(d):
    with open(os.path.join(d, "pattern.json"), encoding="utf-8") as f:
        data = json.load(f)
    checks = data.get("validation", [])
    ok = sum(c["status"] == "OK" for c in checks)
    fabric = ", ".join(f"{name.lower()} {v['need'] / 1000:.2f} m at {v['width'] / 10:.0f} cm width"
                       for name, v in data.get("fabric_mm", {}).items())
    with open(os.path.join(d, "sewing_instructions.md"), encoding="utf-8") as f:
        md = f.read().split("## Sewing instructions", 1)[-1]
    steps = sum(1 for line in md.splitlines() if line[:1].isdigit() and ". " in line[:5])
    return [f"- **Pieces:** {len(data.get('pieces', []))}",
            f"- **Fabric to buy:** {fabric}" if fabric else "",
            f"- **Sewing steps:** {steps}",
            f"- **Sewability checks:** {ok} of {len(checks)} OK"]


def _preview(d):
    files = sorted(os.listdir(d), key=lambda f: "roll" not in f)       # roll preview first
    return next(f for f in files if f.endswith("_preview.png"))


def make_readmes():
    ex = os.path.join(ROOT, "examples")
    for folder, title, prompt, blurb in EXAMPLES:
        d = os.path.join(ex, folder)
        lines = [f"# {title}", "", f"> *\"{prompt}\"*", "", blurb, "",
                 f'<img src="{_preview(d)}" alt="Preview of the print file" width="500">', "",
                 "## At a glance", "", *[x for x in _facts(d) if x], "",
                 "## Cutting layout", "", '<img src="cutting_layout.png" alt="Cutting layout" width="700">', ""]
        if folder.startswith("5_"):
            lines += ["## Sewing booklet", "", "<table><tr>",
                      *[f'<td><img src="../../docs/images/{n}.png" alt="{n}"></td>'
                        for n in ("booklet_cover", "booklet_parts", "booklet_steps")],
                      "</tr></table>", ""]
        lines += ["## Files", "", *_file_rows(d), "",
                  "Print the PDF at **100 % / actual size** and check the 5 × 5 cm square before cutting.", ""]
        with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    d = os.path.join(ex, "3_photo_mode_b")
    with open(os.path.join(d, "round_trip_comparison.md"), encoding="utf-8") as f:
        table = [x for x in f.read().splitlines() if x.startswith("|")]
    lines = ["# Joggers copied from a photo", "",
             "> *\"Here is a photo of my son's favourite joggers next to the reference card, make me a "
             "pattern from it.\"*", "",
             "The garment lies flat next to the printable [reference card](../../assets/reference-card.pdf). "
             "Claude straightens the photo, finds the outline, measures it, fits the pattern model to "
             "the measurements and drafts a new pattern. Here the photo is synthetic, made from a known "
             "pattern (joggers size 116), so the result can be compared with the truth.", "",
             "<table><tr>", '<td><img src="photo_flat_with_reference_card.jpg" alt="Photo"></td>',
             '<td><img src="project/overlay_measurement.png" alt="Measured outline"></td>',
             "</tr><tr><td>The photo</td><td>What Claude measured</td></tr></table>", "",
             "## How close is the copy?", "", *table, "",
             "## The rebuilt pattern", "",
             f'<img src="pattern/{_preview(os.path.join(d, "pattern"))}" alt="Rebuilt pattern" width="500">', "",
             *[x for x in _facts(os.path.join(d, "pattern")) if x], "",
             "## Files", "", "| File | What it is |", "|---|---|",
             "| [`photo_flat_with_reference_card.jpg`](photo_flat_with_reference_card.jpg) | The input photo |",
             "| [`project/overlay_measurement.png`](project/overlay_measurement.png) | Outline and measurements drawn on the photo |",
             "| [`project/reverse_report.md`](project/reverse_report.md) | Measurements, fitted values and deviations |",
             "| [`project/project.json`](project/project.json) | Saved project; can be graded to other sizes |",
             "| [`round_trip_comparison.md`](round_trip_comparison.md) | Original vs. reconstructed measurements |",
             "| [`truth_finished_mm.json`](truth_finished_mm.json) | The true measurements of the original |",
             *_file_rows(os.path.join(d, "pattern"), "pattern/")[2:], ""]
    with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# README pictures: copied or rendered from examples/, shrunk to a web-friendly width.
IMAGES = os.path.join(ROOT, "docs", "images")


def _shrink(src, dst, width=900):
    from PIL import Image, ImageChops
    im = Image.open(src).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if box:                                   # trim white margins, keep 20 px
        m = 20
        im = im.crop((max(box[0] - m, 0), max(box[1] - m, 0),
                      min(box[2] + m, im.width), min(box[3] + m, im.height)))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    if dst.endswith(".jpg"):
        im.save(dst, quality=82, optimize=True)
    else:
        im.save(dst, optimize=True)


def _pdf_page(pdf, page, dst, width=700):
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(page), "-l", str(page), pdf,
                        os.path.join(t, "p")], check=True)
        _shrink(os.path.join(t, sorted(os.listdir(t))[0]), dst, width)


def make_images():
    _reset(IMAGES)
    ex = os.path.join(ROOT, "examples")
    e1, e2 = os.path.join(ex, "1_harem_pants_122_roll610"), os.path.join(ex, "2_harem_pants_122_a4")
    e3, e4 = os.path.join(ex, "3_photo_mode_b"), os.path.join(ex, "4_doll_dress_45cm_a4")
    e5, e6 = os.path.join(ex, "5_hoodie_140_a4"), os.path.join(ex, "6_joggers_nested_98_110_122_roll610")
    jobs = [
        (os.path.join(e1, "harem_pants_size122_roll610_preview.png"), "pattern_roll.png"),
        (os.path.join(e2, "harem_pants_size122_a4_preview.png"), "pattern_a4_tiles.png"),
        (os.path.join(e5, "cutting_layout.png"), "cutting_layout.png"),
        (os.path.join(e4, "doll_dress_45cm_a4_preview.png"), "doll_dress.png"),
        (os.path.join(e6, "joggers_98_110_122_roll610_preview.png"), "nested_sizes.png"),
        (os.path.join(e3, "photo_flat_with_reference_card.jpg"), "photo_input.jpg"),
        (os.path.join(e3, "project", "overlay_measurement.png"), "photo_overlay.jpg"),
    ]
    for src, name in jobs:
        _shrink(src, os.path.join(IMAGES, name))
    booklet = os.path.join(e5, "sewing_instructions.pdf")
    for page, name in [(1, "booklet_cover.png"), (2, "booklet_parts.png"), (4, "booklet_steps.png")]:
        _pdf_page(booklet, page, os.path.join(IMAGES, name))


# 4: doll clothes: a dress for a 45 cm fabric doll, A4 tiles (doll.py)
DOLL_CM = {"height": 45, "chest": 30, "waist": 28, "hip": 31, "head": 32, "arm": 12, "inseam": 14,
           "side_length": 22}


def make_doll_example():
    d = os.path.join(ROOT, "examples", "4_doll_dress_45cm_a4")
    if os.path.isdir(d):
        shutil.rmtree(d)
    GN.run(dict(garment="dress", doll=True, measures_cm=DOLL_CM, formats=["a4"], out=d,
                basename="doll_dress_45cm"), verbose=False)


if __name__ == "__main__":
    what = sys.argv[1:] or ["examples", "results"]
    if "examples" in what:
        make_examples()
    if "doll" in what:
        make_doll_example()
    if "images" in what and "examples" not in what:
        make_images()
        make_readmes()
    if "results" in what:
        make_results()
