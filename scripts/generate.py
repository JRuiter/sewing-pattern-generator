#!/usr/bin/env python3
"""Main script: measurements → drafting → validation → layout → print files → instructions.

Examples:
  python generate.py --garment pants_basic --style harem --size 122 --fabric sweat \
      --format roll610 --out out/harem122
  python generate.py --spec order.json
  python generate.py --project project/project.json --format roll610 --out out/copy

Spec JSON (all fields optional except garment and size/measures):
  {"garment": "pants_basic", "size": 122, "measures_cm": {"hip": 68},
   "options": {"style": "harem", "fabric": "sweat"},
   "formats": ["roll610", "a4"], "out": "out/harem122",
   "fabric_widths_mm": {"Main fabric": 1500, "Rib knit": 700}}

Exit code 2 if the sewability validation reports errors (then NO print files are
written, only the validation report).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import instructions as I  # noqa: E402
import layout as L  # noqa: E402
import measurements as M  # noqa: E402
import render as R  # noqa: E402
import validate as V  # noqa: E402
from garments import get  # noqa: E402


def size_label(size, measures_cm) -> str:
    if size is None:
        return "made to measure"
    system, n = M.parse_size(size)
    lab = {"kids": "size %g", "women": "women's size %g", "men": "men's size %g"}[system] % n
    if measures_cm:
        lab += " (adjusted)"
    return lab


def _basename(pat) -> str:
    lab = pat.size_label.split(" (")[0].replace("size ", "size").replace("'s", "")
    return f"{pat.title.lower().replace(' ', '_')}_{lab.replace(' ', '_').lower()}"


def spec_from_project(path: str, spec: dict | None = None) -> dict:
    """Turn a saved reverse-engineering project (project.json) into a spec."""
    from reverse import store as S
    p = S.load(path)
    out = dict(garment=p["module"], size=p["size_estimate"],
               options={k: v for k, v in p["options"].items() if not k.startswith("_")},
               size_label=f"copied from garment (≈ size {p['size_estimate']})")
    out.update(spec or {})
    out.pop("project", None)
    return out


def draft_from_spec(spec: dict):
    if spec.get("project"):
        spec = spec_from_project(spec["project"], spec)
    mod = get(spec["garment"])
    measures, sources = M.complete_measures(spec.get("measures_cm"), spec.get("size"))
    warn = M.validate_measures(measures)
    pat = mod.draft(measures, spec.get("options", {}))
    pat.size_label = spec.get("size_label") or size_label(spec.get("size"), spec.get("measures_cm"))
    return pat, sources, warn


def run(spec: dict, verbose: bool = True) -> dict:
    out = spec.get("out", "out")
    os.makedirs(out, exist_ok=True)
    pat, sources, warn = draft_from_spec(spec)
    report = V.validate(pat)
    report_md = V.to_markdown(report)
    base = spec.get("basename") or _basename(pat)
    with open(os.path.join(out, "validation_report.md"), "w", encoding="utf-8") as f:
        f.write(report_md)
    result = dict(pattern=pat, report=report, report_md=report_md, files={}, warnings=warn, ok=V.is_ok(report))
    if not V.is_ok(report):
        if verbose:
            print(report_md)
            print("\nVALIDATION FAILED: no print files were written.", file=sys.stderr)
        return result
    files = {}
    formats = spec.get("formats", ["roll610", "a4"])
    master_lay = None
    for fmt in formats:
        f = fmt.lower()
        if f.startswith("roll"):
            width = float(f[4:] or 610)
            try:
                lay = L.layout_roll(pat, width)
            except ValueError as ex:
                if "wider than the roll" not in str(ex):
                    raise
                # Oversized pieces (e.g. an adult circle skirt): tile into roll-wide
                # strips with overlap and glue marks.
                key = f"ROLL{int(width)}"
                L.PAPER[key] = (width, 1200.0)
                lay = L.layout_tiles(pat, key)
                p = os.path.join(out, f"{base}_roll{int(width)}_strips.pdf")
                R.render_tiles_pdf(pat, lay, p)
                n = sum(not t["empty"] for t in lay.tiles)
                files[f"PDF roll {int(width)} mm, {n} strips of 120 cm to glue (piece wider than the roll)"] = p
                warn.append(f"At least one piece is wider than the roll ({width / 10:.0f} cm). "
                            f"It is split across {n} strips with 1 cm overlap; please glue them together.")
                png = os.path.join(out, f"{base}_roll{int(width)}_preview.png")
                R.render_png(pat, lay, png)
                files[f"Preview roll {int(width)} mm"] = png
                master_lay = master_lay or lay
                continue
            p = os.path.join(out, f"{base}_roll{int(width)}.pdf")
            R.render_roll_pdf(pat, lay, p)
            files[f"PDF roll {int(width)} mm ({lay.page_w:.0f} × {lay.page_h:.0f} mm)"] = p
            png = os.path.join(out, f"{base}_roll{int(width)}_preview.png")
            R.render_png(pat, lay, png)
            files[f"Preview roll {int(width)} mm"] = png
            master_lay = master_lay or lay
        elif f in ("a4", "letter"):
            lay = L.layout_tiles(pat, f.upper())
            p = os.path.join(out, f"{base}_{f}_tiled.pdf")
            _, sq_warn = R.render_tiles_pdf(pat, lay, p)
            n = sum(not t["empty"] for t in lay.tiles)
            files[f"PDF {f.upper()} tiles to glue ({n} pages + overview)"] = p
            png = os.path.join(out, f"{base}_{f}_preview.png")
            R.render_png(pat, lay, png)
            files[f"Preview {f.upper()} tiles"] = png
            if master_lay is None:
                master_lay = lay
        elif f in ("a0", "a1"):
            lay, tiled = L.layout_sheets(pat, f.upper())
            p = os.path.join(out, f"{base}_{f}.pdf")
            R.render_sheets_pdf(pat, lay, p, tiled)
            files[f"PDF {f.upper()} ({lay.sheets} sheet(s)" + (", oversized pieces tiled" if tiled else "") + ")"] = p
            png = os.path.join(out, f"{base}_{f}_preview.png")
            R.render_png(pat, lay, png)
            files[f"Preview {f.upper()}"] = png
            master_lay = master_lay or lay
        else:
            raise ValueError(f"Unknown format {fmt}")
    if master_lay is None:
        master_lay = L.layout_roll(pat, 610)
    svg = os.path.join(out, f"{base}_master_1to1.svg")
    R.render_svg(pat, master_lay, svg)
    files["SVG master 1:1"] = svg
    plans = I.fabric_consumption(pat, spec.get("fabric_widths_mm"))
    zp = os.path.join(out, "cutting_layout.png")
    I.render_fabric_png(pat, plans, zp)
    files["Cutting layout"] = zp
    md_path = os.path.join(out, "sewing_instructions.md")
    pdf_path = os.path.join(out, "sewing_instructions.pdf")
    files["Sewing instructions (PDF)"] = pdf_path
    files["Sewing instructions (Markdown)"] = md_path
    md = I.build_markdown(pat, report_md, plans, files, sources)
    if warn:
        md = md.replace("## Body measurements", "## Body measurements\n\n" + "\n".join(f"> ⚠️ {w}" for w in warn), 1)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    I.markdown_to_pdf(md, pdf_path, images=[zp])
    js = os.path.join(out, "pattern.json")
    data = pat.summary()
    data["validation"] = V.to_rows(report)
    data["fabric_mm"] = {k: {"width": v["width"], "need": v["need_mm"]} for k, v in plans.items()}
    with open(js, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    files["Pattern data (JSON)"] = js
    result["files"] = files
    result["plans"] = plans
    if verbose:
        print(report_md)
        print("\nFiles:")
        for k, v in files.items():
            print(f"  {k}: {v}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate a sewing pattern")
    ap.add_argument("--spec", help="JSON file with the order/spec")
    ap.add_argument("--project", help="project.json from photo mode B (reverse engineering)")
    ap.add_argument("--garment", default="pants_basic")
    ap.add_argument("--size")
    ap.add_argument("--measures", help='body measurements in cm as JSON, e.g. \'{"hip": 68}\'')
    ap.add_argument("--style")
    ap.add_argument("--fit")
    ap.add_argument("--fabric")
    ap.add_argument("--stretch", type=float)
    ap.add_argument("--options", help="further options as JSON")
    ap.add_argument("--format", default="roll610,a4", help="roll610, roll914, a4, letter, a1, a0 (comma-separated)")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    if a.spec:
        with open(a.spec, encoding="utf-8") as f:
            spec = json.load(f)
    elif a.project:
        spec = dict(project=a.project, out=a.out, formats=[x.strip() for x in a.format.split(",")])
    else:
        opts = json.loads(a.options) if a.options else {}
        for k in ("style", "fit", "fabric", "stretch"):
            if getattr(a, k) is not None:
                opts[k] = getattr(a, k)
        size = a.size
        if size is not None and size.replace(".", "").isdigit():
            size = float(size)
        spec = dict(garment=a.garment, size=size, options=opts, out=a.out,
                    measures_cm=json.loads(a.measures) if a.measures else None,
                    formats=[x.strip() for x in a.format.split(",")])
    res = run(spec)
    return 0 if res["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
