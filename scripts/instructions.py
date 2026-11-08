"""Sewing instructions, cutting layout and fabric consumption (Markdown + PDF + PNG)."""
from __future__ import annotations

import math
import os

import numpy as np

import adjust as ADJ
import allowance as A
import ease as E
import layout as L
import machines as MC
import measurements as M
import units as U
from i18n import t as T

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


PLAN_PALETTE = ["#cfe2f3", "#fce5cd", "#d9ead3", "#ead1dc", "#fff2cc", "#d0e0e3", "#f4cccc"]


def render_fabric_png(pattern, plans, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(plans)
    # figure sized to the fabrics (equal scale for all panels), so the plan fills the picture
    spans = [(pl["width"] + 140.0, pl["length"] + 110.0) for pl in plans.values()]
    tot_w = sum(w for w, _ in spans)
    max_h = max(h for _, h in spans)
    fig_w = min(11.0, max(4.5, 3.2 * n + tot_w / 600.0))
    fig_h = min(13.0, max(3.6, fig_w * max_h / tot_w + 0.8))
    fig, axs = plt.subplots(1, n, figsize=(fig_w, fig_h), squeeze=False,
                            gridspec_kw=dict(width_ratios=[w for w, _ in spans]))
    for ax, (fab, pl) in zip(axs[0], plans.items()):
        draw_plan(ax, pattern, fab, pl)
    fig.suptitle(T("Cutting layout") + f" · {T(pattern.title)} {T(pattern.size_label)}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def stretch_pieces(pattern) -> list:
    """Pieces whose stretch has to run along their length (bands, cuffs, waistbands of rib)."""
    return [pc for pc in pattern.pieces if L.fabric_group(pc) == "Rib knit" or getattr(pc, "stretch_dir", "")]


def draw_plan(ax, pattern, fab, pl, compact: bool = False):
    """One fabric of the cutting layout into ax (the PNG, and the cutting step of the booklet).

    compact: smaller labels and a one-line title, for the booklet."""
    import matplotlib.pyplot as plt
    units = U.of(pattern)
    fs_small = 4.5 if compact else 6
    W, H = pl["width"], pl["length"]
    folded = pl.get("mode") == "folded"
    fl = min(pl.get("fold_length", 0.0), H) if folded else 0.0
    if folded:
        # folded selvage to selvage: fold on the left, both selvages on the right
        ax.add_patch(plt.Rectangle((0, 0), W / 2, fl, fc="#f0f0f0", ec="#555", lw=1))
        ax.plot([0, 0], [0, fl], color="#c00", lw=1.4, ls=(0, (6, 2, 1, 2)))
        ax.text(-12, fl / 2, T("fold"), rotation=90, fontsize=fs_small, va="center", ha="right", color="#c00")
        ax.text(W / 2 + 8, fl / 2, T("selvages (both layers)"), rotation=90, fontsize=fs_small, va="center")
        if pl.get("single_section"):
            ax.add_patch(plt.Rectangle((0, fl), W, H - fl, fc="#fafafa", ec="#555", lw=1))
            ax.text(W / 2, fl + 12, T("unfolded: single layer"), fontsize=fs_small, ha="center", va="top",
                    style="italic")
    else:
        ax.add_patch(plt.Rectangle((0, 0), W, H, fc="#fafafa", ec="#555", lw=1))
    rep = pl.get("repeat")
    if rep:
        # stripes (and the vertical lines of checks) drawn lightly over the fabric
        sections = [(0.0, fl, W / 2)] if folded else [(0.0, H, W)]
        if folded and pl.get("single_section"):
            sections.append((fl, H, W))
        for y0, y1, w in sections:
            y = y0
            while y <= y1 + 1e-6:
                ax.plot([0, w], [y, y], color="#3d6fb4", lw=0.4, alpha=0.6, zorder=3)
                y += rep[1]
            if pl.get("print") == "plaid":
                x = 0.0
                while x <= w + 1e-6:
                    ax.plot([x, x], [y0, y1], color="#3d6fb4", lw=0.4, alpha=0.6, zorder=3)
                    x += rep[0]
    for p in pl["placements"]:
        ring = L.placed_ring(pl["rings"][p.index], p)
        pi, k = pl["meta"][p.index]
        ax.fill(ring[:, 0], ring[:, 1], fc=PLAN_PALETTE[pi % len(PLAN_PALETTE)], ec="k", lw=0.6,
                alpha=0.85 if rep else 1.0)
        c = ring.mean(axis=0)
        nm = T(pattern.pieces[pi].name).split(" (")[0]
        if p.layers == 2:
            nm += " ×2"
        elif p.pinned:
            nm += " " + T("(on fold)")
        elif pattern.pieces[pi].on_fold:
            nm += " " + T("(unfolded)")
        # "flipped" only matters for a single layer: through both layers it is a mirrored pair anyway
        if p.mirrored and p.layers == 1 and not p.pinned:
            nm += " " + T("(flipped)")
        w_piece = float(np.ptp(ring[:, 0]))
        fs = (6 if w_piece > 0.12 * W else 4.5) * (0.75 if compact else 1.0)
        ax.text(c[0], c[1], nm, fontsize=fs, ha="center", va="center", wrap=True)
        mp = (pl.get("match_pts") or [None] * len(pl["rings"]))[p.index]
        if rep and mp and mp[0] is not None:
            q = p.apply(np.array([mp[0][0]]))[0]
            ax.plot([q[0]], [q[1]], marker="^", color="#c00", ms=4.5, zorder=5)
    if pl.get("nap"):
        ax.annotate("", xy=(W + 22, H * 0.45), xytext=(W + 22, H * 0.15),
                    arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#7a4a1e"))
        label = {"one_way": "One-way print ↓, all pieces top end up",
                 "stripes": "Stripes: every ▲ on the same stripe, all pieces top end up",
                 "plaid": "Checks: every ▲ on the same line, all pieces top end up"}.get(
            pl.get("print"), "Nap ↓, all pieces waist up")
        ax.text(W / 2, -22, T(label), fontsize=fs_small + 1, ha="center", va="bottom", color="#7a4a1e",
                fontweight="bold")
    # a folded fabric is drawn half as wide: the grainline arrow goes next to it, not into empty space
    R = W / 2 if folded and not pl.get("single_section") else W
    ax.annotate("", xy=(R + 40, H * 0.8), xytext=(R + 40, H * 0.2),
                arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(R + 55, H / 2, T("grainline / selvage"), rotation=90, fontsize=fs_small, va="center")
    if fab == "Rib knit":
        # rib: the ribs run along the grain, the bands must stretch along their length (across the fabric)
        ax.annotate("", xy=(R * 0.85, H + 18), xytext=(R * 0.15, H + 18),
                    arrowprops=dict(arrowstyle="<->", lw=1.0, color="#2e7d32"))
        ax.text(R / 2, H + 24, T("stretch: along the bands"), fontsize=fs_small, ha="center", va="top",
                color="#2e7d32")
    ax.set_xlim(-30, R + 90)
    ax.set_ylim(H + (55 if fab == "Rib knit" else 30), -60)
    ax.set_aspect("equal")
    ax.axis("off")
    how = T("folded (double layer)") if folded else T("single layer")
    if compact:
        ax.set_title(f"{T(fab)} · {U.fabric_width(W, units)} · {how}", fontsize=6.5)
    else:
        ax.set_title(f"{T(fab)}: " + T(f"{U.fabric_width(W, units)} wide") + f", {how}\n"
                     + T("needed") + f" ≈ {U.fabric_length(pl['need_mm'], units)}",
                     fontsize=8)


def layout_text(pl, units: str = "metric") -> str:
    if pl.get("mode") == "folded":
        t = T("folded selvage to selvage, cut on fold pieces at the fold")
    else:
        t = T("single layer")
    pr = pl.get("print")
    if pr in ("one_way", "stripes", "plaid"):
        t += T({"one_way": "; one-way print: all pieces with the top end towards the same end, none turned round",
                "stripes": "; stripes: all pieces top end up, matched at the seams",
                "plaid": "; checks: all pieces top end up, matched along and across"}[pr])
    elif pl.get("nap"):
        t += T("; nap: all pieces with the waist towards the same end, none turned round")
    alt = pl.get("alternative")
    t += T(", incl. 10 % for shrinkage")
    if alt:
        other = T("folded") if alt["mode"] == "folded" else T("single layer")
        t += "; " + other + " " + T(f"would need {U.fabric_length(alt['need_mm'], units)}")
    return t


def print_text(plans, units: str = "metric") -> str | None:
    """How to lay out stripes and checks so they meet at the seams."""
    pl = next((p for p in plans.values() if p.get("repeat")), None)
    if pl is None:
        return None
    rep = pl["repeat"]
    plaid = pl.get("print") == "plaid"
    t = (f"**{T('Matching stripes and checks')}** "
         + T(f"(repeat {U.length(rep[1], units)}): ") +
         T("lay the fabric out flat in a single layer, right side up, and straighten the cut end along one "
           "stripe. Every main piece has a red ▲ in the cutting layout: the hem corner at the side seam, the "
           "underarm point of the sleeve, the bottom of the hood seam. Place each ▲ exactly on the same "
           "dominant stripe (as shown, a whole number of repeats apart); then the stripes continue across "
           "the side seams, the inside leg seams and from the body into the sleeves."))
    if plaid:
        t += " " + T("For checks, also put the centre line of each piece (centre front/back, the grainline of "
                     "legs and sleeves) on the same dominant vertical line.")
    if pl.get("mode") == "folded":
        t += " " + T("Folded: before cutting, pin both layers together stripe on stripe.")
    t += " " + T("Pockets, bands and facings are not matched; cut patch pockets after placing them on the "
                 "garment piece, or on the bias as a contrast. One repeat extra is included in the amount.")
    return t


def fold_text(pattern, plans) -> str | None:
    """How to cut the pieces marked "place on fold", for the layouts actually used."""
    names = [T(p.name) for p in pattern.pieces if p.on_fold]
    if not names:
        return None
    t = (f"**{T('Cut on fold')}** ({', '.join(names)}): " + T("the paper piece is only one half. Its fold edge "
         "(dash-dot line, bracket arrows \"PLACE ON FOLD\") is the centre of the piece: it gets no "
         "seam allowance and is never cut."))
    modes = {pl.get("mode") for pl in plans.values()}
    unfolded = "single" in modes or any(pl.get("single_section") for pl in plans.values())
    if "folded" in modes:
        t += " " + T("On the folded fabric, lay the fold edge exactly on the fabric fold, pin it and cut "
                     "through both layers; opened out you get the whole piece.")
    if unfolded:
        t += " " + T("Where the cutting layout shows a piece \"(unfolded)\" on a single layer, fold the fabric "
                     "along the grain just wide enough for the piece and place the fold edge on that fold, or "
                     "trace the paper piece, flip it over along the fold edge and trace the second half.")
    return t


def piece_table(pattern):
    rows = ["| " + " | ".join(T(h) for h in ("Piece", "Cutting", "Fabric", "Seam allowance")) + " |",
            "|---|---|---|---|"]
    for p in pattern.pieces:
        rows.append(f"| {T(p.name)} | {p.cut_text()} | {T(p.fabric)} | {p.sa_text(U.of(pattern))} |")
    return "\n".join(rows)


def finished_table(pattern):
    from garments import get
    mod = get(pattern.garment)
    labels = getattr(mod, "FINISHED_LABELS", {})
    before = pattern.options.get("_finished_before") if isinstance(pattern.options, dict) else None
    u = U.of(pattern)
    if before:
        rows = ["| " + " | ".join(T(h) for h in ("Finished measurement", "Before", "After", "Change")) + " |",
                "|---|---|---|---|"]
    else:
        rows = ["| " + T("Finished measurement") + " | " + T("Value") + " |", "|---|---|"]
    for k, v in pattern.finished.items():
        lab = T(labels.get(k, (k,))[0])
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
    rows = ["| " + " | ".join(T(h) for h in ("Body measurement", "Value", "Source")) + " |", "|---|---|---|"]
    keys = ["height", "chest", "waist", "hip", "head", "neck", "inseam", "side_length", "arm",
            "back_length", "shoulder", "thigh", "ankle"]
    for k in keys:
        if k in pattern.measures:
            src = (sources or {}).get(k, "table")
            rows.append(f"| {T(M.LABELS.get(k, k))} | {U.length(pattern.measures[k], U.of(pattern))} | {T(src)} |")
    return "\n".join(rows)


def sewing_steps(pattern):
    from garments import get
    mod = get(pattern.garment)
    if hasattr(mod, "sewing_steps"):
        return mod.sewing_steps(pattern)
    return ["Sew the pieces right sides together, matching the notches."]


def all_steps(pattern, plans=None) -> list[str]:
    """Every step as one line of text (preparation included), numbered like the booklet."""
    import steps as ST
    return ST.as_texts(ST.assembly(pattern, plans), pattern.options)


def instructions_pdf(pattern, md: str, path: str, plans, steps, images=None) -> str:
    """sewing_instructions.pdf: the illustrated booklet, then the reference pages
    (printing, measurements, pieces, fabric, validation report) typeset from the Markdown."""
    import tempfile

    from pypdf import PdfWriter

    import booklet as B
    ref_md = _without_section(md, "## " + T("Sewing instructions"))
    with tempfile.TemporaryDirectory() as tmp:
        bk = B.build(pattern, os.path.join(tmp, "booklet.pdf"), plans, steps)
        ref = markdown_to_pdf(ref_md, os.path.join(tmp, "reference.pdf"), images=images,
                              base_dir=os.path.dirname(path))
        w = PdfWriter()
        for p in (bk, ref):
            w.append(p)
        w.add_metadata({"/Title": f"{T(pattern.title)} – " + T("sewing instructions")})
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
    u = U.of(pattern)
    lines = [f"# {T(pattern.title)} · {T(pattern.size_label)}", "",
             f"*{E.describe(o.get('fit', 'normal'), o.get('fabric', 'jersey'), o.get('stretch'))}* · "
             + T("original parametric draft. The pattern is yours to use."), "",
             "> " + T("**Important:** With a new pattern, first sew a **test garment** from inexpensive fabric "
                      "with similar stretch and check the fit."), "",
             "## " + T("Files"), ""]
    for k, v in files.items():
        lines.append(f"- {T(k)}: `{os.path.basename(v)}`")
    lines += ["", "## " + T("Printing"), "",
              "- " + T("Always print at **100 % / \"Actual size\"** (not \"Fit to page\")."),
              "- " + (T("Measure the **5 × 5 cm** control square (or the **1 inch** square) before you cut.")
                      if u == "imperial" else T("Measure the **5 × 5 cm** control square before you cut.")),
              "- " + T("Plotter (610 mm roll): the page is 600 mm wide in portrait. In the print dialog choose "
                       "a custom paper size with exactly this width and length, and turn rotation/scaling off."),
              "", "## " + T("Body measurements"), "", measures_table(pattern, sources), "",
              "## " + T("Finished measurements (virtually sewn)"), "", finished_table(pattern), ""]
    adj = ADJ.markdown(pattern)
    if adj:
        lines += ["## " + T("Fit adjustments (from the test garment)"), "", adj, "",
                  T("The adjustments are saved in `pattern.json` and are applied again when you "
                    "generate this pattern from it (also in another size)."), ""]
    lines += ["## " + T("Pattern pieces"), "", piece_table(pattern), "",
              "## " + T("Fabric needed"), ""]
    for fab, pl in plans.items():
        lines.append(f"- **{T(fab)}:** " + T(f"about {U.fabric_length(pl['need_mm'], u)} at "
                     f"{U.fabric_width(pl['width'], u)} width") + f" ({layout_text(pl, u)})")
        if pl.get("note"):
            lines.append(f"  - ⚠️ {T(pl['note'])}")
        if pl.get("print_note"):
            lines.append(f"  - ⚠️ {T(pl['print_note'])}")
    for n in pattern.notes:
        lines.append(f"- {T(n)}")
    lines += ["", T("Cutting layout: see `cutting_layout.png` (grainline arrow parallel to the selvage, "
                    "\"flipped\" = place the piece face down, \"×2\" = cut through both layers of the folded "
                    "fabric, which gives a mirrored pair, \"(unfolded)\" = cut-on-fold piece shown opened out)."), ""]
    ft = fold_text(pattern, plans)
    if ft:
        lines += [ft, ""]
    pt = print_text(plans, u)
    if pt:
        lines += [pt, ""]
    mach = MC.markdown(pattern)
    if mach:
        lines += ["## " + T("Your machines"), "", mach, ""]
    lines += ["## " + T("Sewing instructions"), "",
              T("The printed instructions (`sewing_instructions.pdf`) show every step as a picture of your "
                "pieces: parts list, tools, then one action per step."), "",
              (T("Seam allowance is included in the pattern (see table).") + " " if A.has_allowance(pattern) else
               T("**The pattern has NO seam allowance.** Add the allowances from the table when you cut.") + " ")
              + (T("Use a jersey/stretch needle for jersey and sweat.") if knit else ""), ""]
    for i, s in enumerate(all_steps(pattern, plans), 1):
        lines.append(f"{i}. {s}")
        if step_images and i in step_images:
            lines.append(f"   ![{T('Step')} {i}]({step_images[i]})")
    lines += ["", "## " + T("Validation report"), "", report_md, ""]
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
    head = ("| " + " | ".join(T(h) for h in ("Size", "Line", "Fabric needed")) + " | "
            + " | ".join(T(labels.get(k, (k,))[0]) for k in keys) + " |")
    rows = [head, "|" + "---|" * (3 + len(keys))]
    data = []
    for n in nested.nest:
        p = n["pattern"]
        plans = fabric_consumption(p, widths, mode)
        fab = "; ".join(f"{T(k)}: {U.fabric_length(v['need_mm'], u)}" for k, v in plans.items())
        line = f"{T(COLOR_NAMES[n['layer']])}, {T(DASH_NAMES[n['layer']])}"
        rows.append(f"| {T(p.size_label)} | {line} | {fab} | "
                    + " | ".join(U.length(p.finished[k], u) for k in keys) + " |")
        data.append({"size": p.size_label, "layer": f"Size {n['label']}",
                     "finished_mm": {k: round(v, 1) for k, v in p.finished.items()},
                     "fabric_mm": {k: v["need_mm"] for k, v in plans.items()}})
    sec = ["## " + T("Sizes in this pattern (nested)"), "",
           T("All sizes are drawn on top of each other, aligned at the same construction point. Every "
           "size has its own colour and line and its own **PDF layer**: in Acrobat/Reader open the "
           "*Layers* panel and switch off the sizes you do not need before printing. Cut along the "
           "line of your size. Sizes can be blended: e.g. width of one size, length of another, by "
           "drawing a smooth line between the two outlines."), "", *rows, "",
           T("Fabric, finished measurements and sewing steps below refer to the largest size") +
           f" ({T(nested.nest_big.size_label)}); " + T("the validation report has one table per size."), ""]
    lines = md.splitlines()
    first = lines[0].split(" · ")[0] + " · " + T(nested.size_label)
    md = "\n".join([first] + lines[1:])
    pp = "## " + T("Pattern pieces")
    md = md.replace(pp, "\n".join(sec) + "\n" + pp, 1)
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
        # colour emoji are not in the embedded font: plain symbols in colour instead of empty boxes
        t = (t.replace("✅", "<font color='#2e7d32'>✓</font>").replace("❌", "<font color='#c62828'>✗</font>")
             .replace("⚠️", "<font color='#b8860b'>⚠</font>").replace("\ufe0f", ""))
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
                            topMargin=15 * mm, bottomMargin=15 * mm, title=T("Sewing instructions"))
    doc.build(story)
    return path
