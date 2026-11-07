"""IKEA-style sewing booklet (vector PDF): cover, parts and tools, numbered steps.

Page 1   cover: name, size, all parts drawn with their letters
Page 2   what you need: parts list (letter, outline, how many, on fold), fabric and notions,
         the machines and tools the steps use, with the stitch settings
Page 3+  the steps, six per page: big number, one action, the diagram from the real pieces,
         one line of detail, the machine and stitch, ×2 when it is done twice

Everything is drawn with matplotlib (vector output via PdfPages, DejaVu Sans).
"""
from __future__ import annotations

import textwrap

import numpy as np

import diagrams as DG
import ease as E
import steps as S
import units as U

PAGE = (8.27, 11.69)            # A4 portrait, inches
INK = DG.INK
GREY = "#777777"
LIGHT = "#e6e6e6"
STEPS_PER_PAGE = 6
NOTION_WORDS = ("elastic", "zip", "velcro", "snap", "button", "drawstring", "cord", "binding")


def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width)) if text else ""


def _header(fig, pattern, page_no: int, title: str = ""):
    fig.text(0.06, 0.965, f"{pattern.title} · {pattern.size_label}".strip(" ·"), fontsize=8, color=GREY,
             va="top")
    if title:
        fig.text(0.5, 0.965, title, fontsize=8, color=GREY, va="top", ha="center")
    fig.text(0.94, 0.965, str(page_no), fontsize=8, color=GREY, va="top", ha="right")
    fig.add_artist(_line(fig, 0.06, 0.94, 0.952))
    fig.text(0.5, 0.02, "Original parametric draft · sew a test garment first", fontsize=6.5, color="#aaa",
             ha="center")


def _line(fig, x0, x1, y, color=LIGHT, lw=0.8):
    from matplotlib.lines import Line2D
    return Line2D([x0, x1], [y, y], transform=fig.transFigure, color=color, lw=lw)


def _pack(rings, aspect: float, gap: float, label_h: float = 0.0):
    """Shelf packing of the outlines into a box of the given width/height ratio.
    Returns offsets (to add to each ring) and the overall (w, h)."""
    dims = [(np.ptp(r[:, 0]), np.ptp(r[:, 1]) + label_h) for r in rings]
    order = sorted(range(len(rings)), key=lambda i: -dims[i][1])
    area = sum((w + gap) * (h + gap) for w, h in dims)
    best = None
    for f in np.linspace(0.6, 2.2, 17):
        max_w = max(max(w for w, _ in dims), np.sqrt(area * aspect) * f)
        offs = [None] * len(rings)
        x = y = row_h = 0.0
        width = 0.0
        for i in order:
            w, h = dims[i]
            if x > 0 and x + w > max_w:
                y -= row_h + gap
                x, row_h = 0.0, 0.0
            r = rings[i]
            offs[i] = np.array([x - r[:, 0].min(), y - h + label_h - r[:, 1].min()])
            x += w + gap
            row_h = max(row_h, h)
            width = max(width, x - gap)
        height = -y + row_h
        scale = min(aspect / width, 1.0 / height) if width and height else 0
        if best is None or scale > best[0]:
            best = (scale, offs, (width, height))
    return best[1], best[2]


def _parts_axes(fig, pattern, rect, label_size=9, names=True):
    """All pieces (opened out if cut on the fold), packed, each with its letter (and name)."""
    x0, y0, w, h = rect
    ax = fig.add_axes(rect)
    rings = [DG._unfolded(pc, DG._outline(pc)) for pc in pattern.pieces]
    big = max(max(np.ptp(r, 0)) for r in rings)
    label_h = big * 0.16 if names else 0.0
    offs, (W, H) = _pack(rings, (w * PAGE[0]) / (h * PAGE[1]), big * 0.08, label_h)
    let = DG.letters(pattern)
    for pc, r, off in zip(pattern.pieces, rings, offs):
        rr = r + off
        DG._fill(ax, rr, wrong=False)
        DG._piece_label(ax, pattern, pc, rr, size=label_size)
        if names:
            cx = (rr[:, 0].min() + rr[:, 0].max()) / 2
            ax.text(cx, rr[:, 1].min() - big * 0.02, f"{let[pc.key]}  " + _wrap(pc.name, 24),
                    ha="center", va="top", fontsize=7.2, fontweight="bold")
            ax.text(cx, rr[:, 1].min() - big * 0.02 - big * 0.055 * (1 + pc.name.count(" ") // 4),
                    _wrap(f"{pc.cut_text()} · {pc.fabric}", 30), ha="center", va="top", fontsize=6.3,
                    color=GREY)
    ax.set_xlim(-big * 0.05, max(W, H * w * PAGE[0] / (h * PAGE[1])) + big * 0.05)
    ax.set_ylim(-max(H, W * h * PAGE[1] / (w * PAGE[0])) - big * 0.05, big * 0.05)
    ax.set_aspect("equal", anchor="NW")
    ax.axis("off")


def _parts_list(fig, pattern, x0, y_top, w, cols=5) -> float:
    """IKEA parts list: one cell per part, each drawn to fit its cell; returns the height used."""
    pcs = pattern.pieces
    let = DG.letters(pattern)
    cw = w / cols
    ch = 0.105
    for i, pc in enumerate(pcs):
        cx, cy = i % cols, i // cols
        x, y = x0 + cx * cw, y_top - (cy + 1) * ch
        ax = fig.add_axes((x + cw * 0.12, y + ch * 0.36, cw * 0.76, ch * 0.6))
        r = DG._unfolded(pc, DG._outline(pc))
        DG._fill(ax, r)
        DG._finish_axes(ax, [r], pad=0.04)
        fig.text(x + cw * 0.47, y + ch * 0.32, f"{let[pc.key]}", fontsize=11, fontweight="bold", ha="right",
                 va="top")
        fig.text(x + cw * 0.53, y + ch * 0.315, f"{pc.cut_count}×", fontsize=9.5, fontweight="bold",
                 ha="left", va="top", color=DG.ACCENT[1])
        fig.text(x + cw * 0.5, y + ch * 0.17, _wrap(pc.name, 26), fontsize=6.6, ha="center", va="top")
        if pc.on_fold:
            fig.text(x + cw * 0.5, y + ch * 0.04, "cut on fold", fontsize=6, ha="center", va="top",
                     color=GREY)
    return int(np.ceil(len(pcs) / cols)) * ch


def cover(pdf, pattern, n_steps: int):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=PAGE)
    title = pattern.title.upper()
    fig.text(0.06, 0.92, title, fontsize=min(34.0, 34.0 * 20 / max(len(title), 1)), fontweight="bold",
             va="top")
    fig.text(0.06, 0.865, pattern.size_label, fontsize=16, va="top", color=GREY)
    o = pattern.options
    fit = E.describe(o.get("fit", "normal"), o.get("fabric", "jersey"), o.get("stretch"))
    fig.text(0.06, 0.835, fit, fontsize=9, va="top", color=GREY)
    _parts_axes(fig, pattern, (0.06, 0.16, 0.88, 0.62), label_size=11, names=False)
    fig.text(0.06, 0.1, f"{len(pattern.pieces)} parts · {n_steps} steps", fontsize=11, fontweight="bold")
    fig.text(0.06, 0.075, "Read the steps once before you start. Every picture is drawn from your "
             "pattern pieces.", fontsize=8, color=GREY)
    _legend(fig, 0.06, 0.04)
    pdf.savefig(fig)
    plt.close(fig)


def _legend(fig, x, y):
    """Symbol key: right side, wrong side, stitch line, pin, notch."""
    import matplotlib.pyplot as plt  # noqa: F401
    items = [("right side", "right"), ("wrong side", "wrong"), ("stitch", "stitch"), ("pin", "pin"),
             ("notch: match", "notch")]
    for i, (lab, kind) in enumerate(items):
        ax = fig.add_axes((x + i * 0.17, y - 0.008, 0.035, 0.02))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        if kind in ("right", "wrong"):
            DG._fill(ax, np.array([[0.05, 0.1], [0.95, 0.1], [0.95, 0.9], [0.05, 0.9]]), wrong=kind == "wrong")
        elif kind == "stitch":
            DG._stitch(ax, [[0.0, 0.5], [1.0, 0.5]])
        elif kind == "pin":
            ax.plot([0.15, 0.75], [0.5, 0.5], color=DG.PIN, lw=1.2)
            ax.plot([0.8], [0.5], "o", ms=4, color=DG.PIN_HEAD)
        else:
            ax.plot([0.5, 0.5], [0.0, 1.0], color=INK, lw=1.4)
        fig.text(x + i * 0.17 + 0.04, y, lab, fontsize=7, va="center")


def needs_page(pdf, pattern, steps, plans, page_no: int):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=PAGE)
    _header(fig, pattern, page_no, "What you need")
    fig.text(0.06, 0.925, "Parts", fontsize=14, fontweight="bold", va="top")
    hp = _parts_list(fig, pattern, 0.06, 0.9, 0.88)
    y = 0.88 - hp
    u = U.of(pattern)
    fig.text(0.06, y, "Fabric and notions", fontsize=14, fontweight="bold", va="top")
    y -= 0.035
    lines = []
    for fab, pl in (plans or {}).items():
        lines.append(f"{fab}: {U.fabric_length(pl['need_mm'], u)} at {U.fabric_width(pl['width'], u)} width")
    for n in pattern.notes:
        if any(w in n.lower() for w in NOTION_WORDS):
            lines.append(n)
    lines.append("Polyester sewing thread to match")
    for ln in lines:
        fig.text(0.08, y, "•  " + _wrap(ln, 105).replace("\n", "\n    "), fontsize=8, va="top")
        y -= 0.02 * (1 + ln.count("\n") + len(ln) // 105)
    y -= 0.015
    fig.text(0.06, y, "Machines and tools", fontsize=14, fontweight="bold", va="top")
    y -= 0.04
    tools = S.machines_needed(steps, pattern.options)
    extra = [("pins", "Pins or clips"), ("scissors", "Fabric scissors"), ("tape", "Tape measure"),
             ("chalk", "Chalk or a fabric pen")]
    if any(s.data.get("picture") == "elastic" for s in steps):
        extra.append(("safety_pin", "Safety pin"))
    entries = [(t["machine"], t["name"], _tool_detail(steps, pattern, t["machine"])) for t in tools] + \
              [(k, n, "") for k, n in extra]
    col_w = 0.30
    for i, (key, name, detail) in enumerate(entries):
        cx = 0.06 + (i % 3) * col_w
        cy = y - (i // 3) * 0.08
        ax = fig.add_axes((cx, cy - 0.06, 0.06, 0.06))
        DG.draw_machine(ax, key)
        fig.text(cx + 0.075, cy - 0.012, name, fontsize=9, fontweight="bold", va="top")
        if detail:
            fig.text(cx + 0.075, cy - 0.03, _wrap(detail, 34), fontsize=6.6, va="top", color="#444")
    if S.owned_machines(pattern.options) is None:
        fig.text(0.06, 0.06, _wrap("Steps are written for a sewing machine with zigzag. Have an overlocker "
                 "or a coverstitch machine? Tell the generator which machines you own and the steps use "
                 "them.", 120), fontsize=7, color=GREY)
    pdf.savefig(fig)
    plt.close(fig)


def _tool_detail(steps, pattern, machine) -> str:
    seen = []
    for s in steps:
        if not s.stitch:
            continue
        t = S.tool_for(pattern.options, s.stitch, s.data.get("knit"))
        if t.get("machine") == machine and t.get("stitch") and t["stitch"] not in seen:
            seen.append(t["stitch"])
    return "; ".join(seen)


def _panel(fig, pattern, n: int, step: S.Step, rect, prev_section: str):
    x, y, w, h = rect
    from matplotlib.patches import FancyBboxPatch
    fig.add_artist(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.006",
                                  transform=fig.transFigure, fc="none", ec=LIGHT, lw=0.8))
    fig.text(x + 0.012, y + h - 0.008, str(n), fontsize=24, fontweight="bold", va="top", ha="left")
    tx = x + 0.075 if n < 10 else x + 0.09
    if step.section and step.section != prev_section:
        fig.text(tx, y + h - 0.01, step.section.upper(), fontsize=6.5, color=GREY, va="top")
    fig.text(tx, y + h - 0.024, _wrap(step.title, 34), fontsize=10, fontweight="bold", va="top")
    if step.repeat > 1:
        fig.text(x + w - 0.012, y + h - 0.012, f"×{step.repeat}", fontsize=15, fontweight="bold",
                 va="top", ha="right", color=DG.ACCENT[1])
    # diagram
    bottom = 0.075 + (0.018 if step.tip else 0.0)
    ax = fig.add_axes((x + 0.012, y + bottom, w - 0.024, h - 0.07 - bottom))
    DG.draw(ax, pattern, step)
    # text + machine
    fig.text(x + 0.012, y + 0.068, _wrap(step.text, 66), fontsize=7.2, va="top", color="#333",
             linespacing=1.25)
    tool = S.tool_for(pattern.options, step.stitch, step.data.get("knit")) if step.stitch else {}
    if tool:
        iax = fig.add_axes((x + 0.012, y + 0.006, 0.03, 0.022))
        DG.draw_machine(iax, tool["machine"])
        fig.text(x + 0.046, y + 0.017, f"{tool['name']}" + (f": {tool['stitch']}" if tool.get("stitch") else ""),
                 fontsize=6.8, va="center", color="#333")
    if step.tip:
        fig.text(x + 0.012, y + 0.08, "!  " + step.tip, fontsize=6.8, va="center", ha="left",
                 color=DG.ACCENT[0], fontweight="bold")


def step_pages(pdf, pattern, steps, first_page: int) -> int:
    import matplotlib.pyplot as plt
    page = first_page
    prev = ""
    cols, rows = 2, STEPS_PER_PAGE // 2
    mx, top, bottom, gap = 0.05, 0.935, 0.04, 0.012
    pw = (1 - 2 * mx - gap) / cols
    ph = (top - bottom - gap * (rows - 1)) / rows
    for start in range(0, len(steps), STEPS_PER_PAGE):
        fig = plt.figure(figsize=PAGE)
        _header(fig, pattern, page, "Sewing")
        for k, st in enumerate(steps[start:start + STEPS_PER_PAGE]):
            n = start + k + 1
            cx, cy = k % cols, k // cols
            rect = (mx + cx * (pw + gap), top - (cy + 1) * ph - cy * gap, pw, ph)
            _panel(fig, pattern, n, st, rect, prev)
            prev = st.section
        pdf.savefig(fig)
        plt.close(fig)
        page += 1
    return page


def build(pattern, path: str, plans=None, steps: list[S.Step] | None = None) -> str:
    """Write the booklet PDF; returns the path."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    steps = steps if steps is not None else S.assembly(pattern)
    with plt.rc_context({"font.family": "DejaVu Sans", "pdf.fonttype": 42}):
        with PdfPages(path, metadata={"Title": f"{pattern.title} – sewing instructions",
                                      "Creator": "sewing-pattern-generator"}) as pdf:
            cover(pdf, pattern, len(steps))
            needs_page(pdf, pattern, steps, plans, 2)
            step_pages(pdf, pattern, steps, 3)
    return path
