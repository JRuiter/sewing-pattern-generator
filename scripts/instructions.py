"""Sewing instructions, cutting layout and fabric consumption (Markdown + PDF + PNG)."""
from __future__ import annotations

import math
import os

import ease as E
import layout as L
import measurements as M

FABRIC_DEFAULT_WIDTH = {"Main fabric": 1500.0, "Rib knit": 700.0, "Lining": 1400.0}


def fabric_consumption(pattern, widths: dict | None = None):
    widths = {**FABRIC_DEFAULT_WIDTH, **(widths or {})}
    plans = L.layout_fabric(pattern, widths)
    out = {}
    for fab, pl in plans.items():
        knit_extra = 1.10      # 10 % for shrinkage/pre-washing and straightening
        need = math.ceil(pl["length"] * knit_extra / 50.0) * 50.0   # round up to 5 cm
        pl["need_mm"] = need
        out[fab] = pl
    return out


def render_fabric_png(pattern, plans, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(plans)
    fig, axs = plt.subplots(1, n, figsize=(4.2 * n, 7), squeeze=False)
    palette = ["#cfe2f3", "#fce5cd", "#d9ead3", "#ead1dc", "#fff2cc", "#d0e0e3", "#f4cccc"]
    for ax, (fab, pl) in zip(axs[0], plans.items()):
        W, H = pl["width"], pl["length"]
        ax.add_patch(plt.Rectangle((0, 0), W, H, fc="#fafafa", ec="#555", lw=1))
        for p in pl["placements"]:
            ring = L.placed_ring(pl["rings"][p.index], p)
            pi, k = pl["meta"][p.index]
            ax.fill(ring[:, 0], ring[:, 1], fc=palette[pi % len(palette)], ec="k", lw=0.6)
            c = ring.mean(axis=0)
            nm = pattern.pieces[pi].name.split(" (")[0]
            ax.text(c[0], c[1], nm + (" (flipped)" if p.mirrored else ""), fontsize=6, ha="center", va="center")
        ax.annotate("", xy=(W + 40, H * 0.8), xytext=(W + 40, H * 0.2),
                    arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(W + 55, H / 2, "grainline / selvage", rotation=90, fontsize=6, va="center")
        ax.set_xlim(-30, W + 90)
        ax.set_ylim(H + 30, -60)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{fab}: {W / 10:.0f} cm wide, single layer\nneeded ≈ {pl['need_mm'] / 1000:.2f} m",
                     fontsize=8)
    fig.suptitle(f"Cutting layout · {pattern.title} {pattern.size_label}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def piece_table(pattern):
    rows = ["| Piece | Cutting | Fabric | Seam allowance |", "|---|---|---|---|"]
    for p in pattern.pieces:
        rows.append(f"| {p.name} | {p.cut_text()} | {p.fabric} | {p.sa_text()} |")
    return "\n".join(rows)


def finished_table(pattern):
    from garments import get
    mod = get(pattern.garment)
    labels = getattr(mod, "FINISHED_LABELS", {})
    rows = ["| Finished measurement | Value |", "|---|---|"]
    for k, v in pattern.finished.items():
        lab = labels.get(k, (k,))[0]
        rows.append(f"| {lab} | {v / 10:.1f} cm |")
    return "\n".join(rows)


def measures_table(pattern, sources=None):
    rows = ["| Body measurement | Value | Source |", "|---|---|---|"]
    keys = ["height", "chest", "waist", "hip", "head", "neck", "inseam", "side_length", "arm",
            "back_length", "shoulder", "thigh", "ankle"]
    for k in keys:
        if k in pattern.measures:
            src = (sources or {}).get(k, "table")
            rows.append(f"| {M.LABELS.get(k, k)} | {pattern.measures[k] / 10:.1f} cm | {src} |")
    return "\n".join(rows)


def sewing_steps(pattern):
    from garments import get
    mod = get(pattern.garment)
    if hasattr(mod, "sewing_steps"):
        return mod.sewing_steps(pattern)
    return ["Sew the pieces right sides together, matching the notches."]


def build_markdown(pattern, report_md, plans, files: dict, sources=None):
    o = pattern.options
    fab_label, stretch, knit = E.fabric_info(o.get("fabric", "jersey"), o.get("stretch"))
    lines = [f"# {pattern.title} · {pattern.size_label}", "",
             f"*{E.describe(o.get('fit', 'normal'), o.get('fabric', 'jersey'), o.get('stretch'))}* · "
             "original parametric draft. The pattern is yours to use.", "",
             "> **Important:** With a new pattern, first sew a **test garment** from inexpensive fabric "
             "with similar stretch and check the fit.", "",
             "## Files", ""]
    for k, v in files.items():
        lines.append(f"- {k}: `{os.path.basename(v)}`")
    lines += ["", "## Printing", "",
              "- Always print at **100 % / \"Actual size\"** (not \"Fit to page\").",
              "- Measure the **5 × 5 cm** control square before you cut.",
              "- Plotter (610 mm roll): the page is 600 mm wide in portrait. In the print dialog choose "
              "a custom paper size with exactly this width and length, and turn rotation/scaling off.",
              "", "## Body measurements", "", measures_table(pattern, sources), "",
              "## Finished measurements (virtually sewn)", "", finished_table(pattern), "",
              "## Pattern pieces", "", piece_table(pattern), "",
              "## Fabric needed", ""]
    for fab, pl in plans.items():
        lines.append(f"- **{fab}:** about {pl['need_mm'] / 1000:.2f} m at {pl['width'] / 10:.0f} cm width "
                     f"(single layer, incl. 10 % for shrinkage)")
        if pl.get("note"):
            lines.append(f"  - ⚠️ {pl['note']}")
    for n in pattern.notes:
        lines.append(f"- {n}")
    lines += ["", "Cutting layout: see `cutting_layout.png` (grainline arrow parallel to the selvage, "
              "\"flipped\" = place the piece face down).", "",
              "## Sewing instructions", "",
              "Seam allowance is included in the pattern (see table). "
              + ("Use a jersey/stretch needle for jersey and sweat." if knit else ""), ""]
    for i, s in enumerate(["**Prepare:** pre-wash the fabric, cut out the pieces, snip the notches "
                           "3–4 mm deep."] + sewing_steps(pattern), 1):
        lines.append(f"{i}. {s}")
    lines += ["", "## Validation report", "", report_md, ""]
    return "\n".join(lines)


def markdown_to_pdf(md: str, path: str, images: list[str] | None = None):
    """Simple Markdown→PDF typesetting (headings, lists, tables) with an embedded font."""
    import re

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    import render as R
    R.register_fonts()
    base = ParagraphStyle("b", fontName=R.FONT, fontSize=9, leading=12)
    h1 = ParagraphStyle("h1", parent=base, fontName=R.FONT_B, fontSize=16, leading=20, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=base, fontName=R.FONT_B, fontSize=12, leading=16, spaceBefore=8, spaceAfter=4)
    h3 = ParagraphStyle("h3", parent=base, fontName=R.FONT_B, fontSize=10.5, leading=14, spaceBefore=6)
    small = ParagraphStyle("s", parent=base, fontSize=7, leading=8.5)

    def inline(t):
        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
        t = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", t)
        return t.replace("<b>", f"<font name='{R.FONT_B}'>").replace("</b>", "</font>")

    story, table = [], []

    def flush():
        nonlocal table
        if table:
            rows = [r for r in table if not re.match(r"^\|\s*-", r)]
            data = [[Paragraph(inline(c.strip()), small) for c in r.strip().strip("|").split("|")] for r in rows]
            ncol = len(data[0])
            tw = 180 * mm
            t = Table(data, colWidths=[tw / ncol] * ncol, repeatRows=1)
            t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story.append(t)
            story.append(Spacer(1, 4))
            table = []

    for line in md.splitlines():
        if line.startswith("|"):
            table.append(line)
            continue
        flush()
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), h1))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), h2))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), h3))
        elif line.startswith("> "):
            story.append(Paragraph(inline(line[2:]), ParagraphStyle("q", parent=base, leftIndent=8,
                                                                    backColor=colors.Color(1, 0.96, 0.85))))
        elif re.match(r"^(\d+\.|-) ", line):
            story.append(Paragraph(inline(line), ParagraphStyle("li", parent=base, leftIndent=10)))
        elif line.strip():
            story.append(Paragraph(inline(line), base))
        else:
            story.append(Spacer(1, 3))
    flush()
    for img in images or []:
        from PIL import Image as PImage
        w, h = PImage.open(img).size
        tw = 180 * mm
        th = tw * h / w
        if th > 240 * mm:
            th = 240 * mm
            tw = th * w / h
        story.append(Image(img, width=tw, height=th))
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title="Sewing instructions")
    doc.build(story)
    return path
