"""Sewing instructions, cutting layout and fabric consumption (Markdown + PDF + PNG)."""
from __future__ import annotations

import math
import os

import adjust as ADJ
import allowance as A
import ease as E
import layout as L
import machines as MC
import measurements as M
import units as U

FABRIC_DEFAULT_WIDTH = {"Main fabric": 1500.0, "Rib knit": 700.0, "Lining": 1400.0}


def fabric_consumption(pattern, widths: dict | None = None, mode: str = "auto"):
    widths = {**FABRIC_DEFAULT_WIDTH, **(widths or {})}
    plans = L.layout_fabric(pattern, widths, mode=mode)
    out = {}
    for fab, pl in plans.items():
        pl["need_mm"] = need_mm(pl["length"])
        if pl.get("alternative"):
            pl["alternative"]["need_mm"] = need_mm(pl["alternative"]["length"])
        out[fab] = pl
    return out


def need_mm(length: float) -> float:
    """Fabric to buy: +10 % for shrinkage/pre-washing and straightening, rounded up to 5 cm."""
    return math.ceil(length * 1.10 / 50.0) * 50.0


def render_fabric_png(pattern, plans, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(plans)
    fig, axs = plt.subplots(1, n, figsize=(4.2 * n, 7), squeeze=False)
    units = U.of(pattern)
    palette = ["#cfe2f3", "#fce5cd", "#d9ead3", "#ead1dc", "#fff2cc", "#d0e0e3", "#f4cccc"]
    for ax, (fab, pl) in zip(axs[0], plans.items()):
        W, H = pl["width"], pl["length"]
        folded = pl.get("mode") == "folded"
        fl = min(pl.get("fold_length", 0.0), H) if folded else 0.0
        if folded:
            # folded selvage to selvage: fold on the left, both selvages on the right
            ax.add_patch(plt.Rectangle((0, 0), W / 2, fl, fc="#f0f0f0", ec="#555", lw=1))
            ax.plot([0, 0], [0, fl], color="#c00", lw=1.4, ls=(0, (6, 2, 1, 2)))
            ax.text(-12, fl / 2, "fold", rotation=90, fontsize=6, va="center", ha="right", color="#c00")
            ax.text(W / 2 + 8, fl / 2, "selvages (both layers)", rotation=90, fontsize=6, va="center")
            if pl.get("single_section"):
                ax.add_patch(plt.Rectangle((0, fl), W, H - fl, fc="#fafafa", ec="#555", lw=1))
                ax.text(W / 2, fl + 12, "unfolded: single layer", fontsize=6, ha="center", va="top",
                        style="italic")
        else:
            ax.add_patch(plt.Rectangle((0, 0), W, H, fc="#fafafa", ec="#555", lw=1))
        for p in pl["placements"]:
            ring = L.placed_ring(pl["rings"][p.index], p)
            pi, k = pl["meta"][p.index]
            ax.fill(ring[:, 0], ring[:, 1], fc=palette[pi % len(palette)], ec="k", lw=0.6)
            c = ring.mean(axis=0)
            nm = pattern.pieces[pi].name.split(" (")[0]
            if p.layers == 2:
                nm += " ×2"
            elif p.pinned:
                nm += " (on fold)"
            elif pattern.pieces[pi].on_fold:
                nm += " (unfolded)"
            ax.text(c[0], c[1], nm + (" (flipped)" if p.mirrored else ""), fontsize=6, ha="center", va="center")
        if pl.get("nap"):
            ax.annotate("", xy=(W + 22, H * 0.45), xytext=(W + 22, H * 0.15),
                        arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#7a4a1e"))
            ax.text(W / 2, -22, "Nap ↓, all pieces waist up", fontsize=7, ha="center", va="bottom",
                    color="#7a4a1e", fontweight="bold")
        ax.annotate("", xy=(W + 40, H * 0.8), xytext=(W + 40, H * 0.2),
                    arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text(W + 55, H / 2, "grainline / selvage", rotation=90, fontsize=6, va="center")
        ax.set_xlim(-30, W + 90)
        ax.set_ylim(H + 30, -60)
        ax.set_aspect("equal")
        ax.axis("off")
        how = "folded (double layer)" if folded else "single layer"
        ax.set_title(f"{fab}: {U.fabric_width(W, units)} wide, {how}\n"
                     f"needed ≈ {U.fabric_length(pl['need_mm'], units)}",
                     fontsize=8)
    fig.suptitle(f"Cutting layout · {pattern.title} {pattern.size_label}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def layout_text(pl, units: str = "metric") -> str:
    if pl.get("mode") == "folded":
        t = "folded selvage to selvage, cut on fold pieces at the fold"
    else:
        t = "single layer"
    if pl.get("nap"):
        t += "; nap: all pieces with the waist towards the same end, none turned round"
    alt = pl.get("alternative")
    if alt:
        other = "folded" if alt["mode"] == "folded" else "single layer"
        t += f", incl. 10 % for shrinkage; {other} would need {U.fabric_length(alt['need_mm'], units)}"
    else:
        t += ", incl. 10 % for shrinkage"
    return t


def fold_text(pattern, plans) -> str | None:
    """How to cut the pieces marked "place on fold", for the layouts actually used."""
    names = [p.name for p in pattern.pieces if p.on_fold]
    if not names:
        return None
    t = (f"**Cut on fold** ({', '.join(names)}): the paper piece is only one half. Its fold edge "
         "(dash-dot line, bracket arrows \"PLACE ON FOLD\") is the centre of the piece: it gets no "
         "seam allowance and is never cut.")
    modes = {pl.get("mode") for pl in plans.values()}
    unfolded = "single" in modes or any(pl.get("single_section") for pl in plans.values())
    if "folded" in modes:
        t += (" On the folded fabric, lay the fold edge exactly on the fabric fold, pin it and cut "
              "through both layers; opened out you get the whole piece.")
    if unfolded:
        t += (" Where the cutting layout shows a piece \"(unfolded)\" on a single layer, fold the fabric "
              "along the grain just wide enough for the piece and place the fold edge on that fold, or "
              "trace the paper piece, flip it over along the fold edge and trace the second half.")
    return t


def piece_table(pattern):
    rows = ["| Piece | Cutting | Fabric | Seam allowance |", "|---|---|---|---|"]
    for p in pattern.pieces:
        rows.append(f"| {p.name} | {p.cut_text()} | {p.fabric} | {p.sa_text(U.of(pattern))} |")
    return "\n".join(rows)


def finished_table(pattern):
    from garments import get
    mod = get(pattern.garment)
    labels = getattr(mod, "FINISHED_LABELS", {})
    before = pattern.options.get("_finished_before") if isinstance(pattern.options, dict) else None
    u = U.of(pattern)
    if before:
        rows = ["| Finished measurement | Before | After | Change |", "|---|---|---|---|"]
    else:
        rows = ["| Finished measurement | Value |", "|---|---|"]
    for k, v in pattern.finished.items():
        lab = labels.get(k, (k,))[0]
        if before:
            b = before.get(k)
            if b is None:
                rows.append(f"| {lab} | – | {U.length(v, u)} | |")
            else:
                d = v - b
                ch = "" if abs(d) < 0.5 else ("+" if d > 0 else "−") + U.length(abs(d), u)
                rows.append(f"| {lab} | {U.length(b, u)} | {U.length(v, u)} | {ch} |")
        else:
            rows.append(f"| {lab} | {U.length(v, u)} |")
    return "\n".join(rows)


def measures_table(pattern, sources=None):
    rows = ["| Body measurement | Value | Source |", "|---|---|---|"]
    keys = ["height", "chest", "waist", "hip", "head", "neck", "inseam", "side_length", "arm",
            "back_length", "shoulder", "thigh", "ankle"]
    for k in keys:
        if k in pattern.measures:
            src = (sources or {}).get(k, "table")
            rows.append(f"| {M.LABELS.get(k, k)} | {U.length(pattern.measures[k], U.of(pattern))} | {src} |")
    return "\n".join(rows)


def sewing_steps(pattern):
    from garments import get
    mod = get(pattern.garment)
    if hasattr(mod, "sewing_steps"):
        return mod.sewing_steps(pattern)
    return ["Sew the pieces right sides together, matching the notches."]


def all_steps(pattern) -> list[str]:
    """Every step as one line of text (preparation included), numbered like the booklet."""
    import steps as ST
    return ST.as_texts(ST.assembly(pattern), pattern.options)


def instructions_pdf(pattern, md: str, path: str, plans, steps, images=None) -> str:
    """sewing_instructions.pdf: the IKEA-style booklet, then the reference pages
    (printing, measurements, pieces, fabric, validation report) typeset from the Markdown."""
    import tempfile

    from pypdf import PdfWriter

    import booklet as B
    ref_md = _without_section(md, "## Sewing instructions")
    with tempfile.TemporaryDirectory() as tmp:
        bk = B.build(pattern, os.path.join(tmp, "booklet.pdf"), plans, steps)
        ref = markdown_to_pdf(ref_md, os.path.join(tmp, "reference.pdf"), images=images,
                              base_dir=os.path.dirname(path))
        w = PdfWriter()
        for p in (bk, ref):
            w.append(p)
        w.add_metadata({"/Title": f"{pattern.title} – sewing instructions"})
        with open(path, "wb") as f:
            w.write(f)
    return path


def _without_section(md: str, heading: str) -> str:
    out, skip = [], False
    for line in md.splitlines():
        if line.startswith("## "):
            skip = line.startswith(heading)
        if not skip:
            out.append(line)
    return "\n".join(out)


def build_markdown(pattern, report_md, plans, files: dict, sources=None, step_images=None):
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
              ("- Measure the **5 × 5 cm** control square (or the **1 inch** square) before you cut."
               if U.of(pattern) == "imperial" else "- Measure the **5 × 5 cm** control square before you cut."),
              "- Plotter (610 mm roll): the page is 600 mm wide in portrait. In the print dialog choose "
              "a custom paper size with exactly this width and length, and turn rotation/scaling off.",
              "", "## Body measurements", "", measures_table(pattern, sources), "",
              "## Finished measurements (virtually sewn)", "", finished_table(pattern), ""]
    adj = ADJ.markdown(pattern)
    if adj:
        lines += ["## Fit adjustments (from the test garment)", "", adj, "",
                  "The adjustments are saved in `pattern.json` and are applied again when you "
                  "generate this pattern from it (also in another size).", ""]
    lines += ["## Pattern pieces", "", piece_table(pattern), "",
              "## Fabric needed", ""]
    for fab, pl in plans.items():
        lines.append(f"- **{fab}:** about {U.fabric_length(pl['need_mm'], U.of(pattern))} at "
                     f"{U.fabric_width(pl['width'], U.of(pattern))} width ({layout_text(pl, U.of(pattern))})")
        if pl.get("note"):
            lines.append(f"  - ⚠️ {pl['note']}")
    for n in pattern.notes:
        lines.append(f"- {n}")
    lines += ["", "Cutting layout: see `cutting_layout.png` (grainline arrow parallel to the selvage, "
              "\"flipped\" = place the piece face down, \"×2\" = cut through both layers of the folded "
              "fabric, which gives a mirrored pair, \"(unfolded)\" = cut-on-fold piece shown opened out).", ""]
    ft = fold_text(pattern, plans)
    if ft:
        lines += [ft, ""]
    mach = MC.markdown(pattern)
    if mach:
        lines += ["## Your machines", "", mach, ""]
    lines += ["## Sewing instructions", "",
              "The printed instructions (`sewing_instructions.pdf`) show every step as a picture of your "
              "pieces, IKEA style: parts list, tools, then one action per step.", "",
              ("Seam allowance is included in the pattern (see table). " if A.has_allowance(pattern) else
               "**The pattern has NO seam allowance.** Add the allowances from the table when you cut. ")
              + ("Use a jersey/stretch needle for jersey and sweat." if knit else ""), ""]
    for i, s in enumerate(all_steps(pattern), 1):
        lines.append(f"{i}. {s}")
        if step_images and i in step_images:
            lines.append(f"   ![Step {i}]({step_images[i]})")
    lines += ["", "## Validation report", "", report_md, ""]
    return "\n".join(lines)


COLOR_NAMES = ["red", "blue", "green", "purple", "orange", "teal", "brown", "grey"]
DASH_NAMES = ["solid", "long dashes", "short dashes", "dash-dot", "long dashes", "dots", "dash-dot-dot",
              "even dashes"]


def nested_section(md: str, nested, widths=None, mode="auto"):
    """Add the size table of a nested multi-size pattern to the instructions."""
    from garments import get
    labels = getattr(get(nested.garment), "FINISHED_LABELS", {})
    u = U.of(nested.nest_big)
    keys = [k for k in nested.nest_big.finished][:4]
    head = "| Size | Line | Fabric needed | " + " | ".join(labels.get(k, (k,))[0] for k in keys) + " |"
    rows = [head, "|" + "---|" * (3 + len(keys))]
    data = []
    for n in nested.nest:
        p = n["pattern"]
        plans = fabric_consumption(p, widths, mode)
        fab = "; ".join(f"{k}: {U.fabric_length(v['need_mm'], u)}" for k, v in plans.items())
        line = f"{COLOR_NAMES[n['layer']]}, {DASH_NAMES[n['layer']]}"
        rows.append(f"| {p.size_label} | {line} | {fab} | "
                    + " | ".join(U.length(p.finished[k], u) for k in keys) + " |")
        data.append({"size": p.size_label, "layer": f"Size {n['label']}",
                     "finished_mm": {k: round(v, 1) for k, v in p.finished.items()},
                     "fabric_mm": {k: v["need_mm"] for k, v in plans.items()}})
    sec = ["## Sizes in this pattern (nested)", "",
           "All sizes are drawn on top of each other, aligned at the same construction point. Every "
           "size has its own colour and line and its own **PDF layer**: in Acrobat/Reader open the "
           "*Layers* panel and switch off the sizes you do not need before printing. Cut along the "
           "line of your size. Sizes can be blended: e.g. width of one size, length of another, by "
           "drawing a smooth line between the two outlines.", "", *rows, "",
           "Fabric, finished measurements and sewing steps below refer to the largest size "
           f"({nested.nest_big.size_label}); the validation report has one table per size.", ""]
    lines = md.splitlines()
    first = lines[0].split(" · ")[0] + " · " + nested.size_label
    md = "\n".join([first] + lines[1:])
    md = md.replace("## Pattern pieces", "\n".join(sec) + "\n## Pattern pieces", 1)
    return md, data


def markdown_to_pdf(md: str, path: str, images: list[str] | None = None, base_dir: str | None = None):
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
        im = re.match(r"^\s*!\[[^\]]*\]\(([^)]+)\)\s*$", line)
        if im:
            ip = os.path.join(base_dir or os.path.dirname(path), im.group(1))
            if os.path.exists(ip):
                from PIL import Image as PImage
                w, h = PImage.open(ip).size
                tw = 150 * mm
                story.append(Image(ip, width=tw, height=tw * h / w))
            continue
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
