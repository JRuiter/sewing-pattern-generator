"""Illustrated sewing booklet (vector PDF).

Page 1    cover: name, size/fit/fabric in one line, the finished garment from the front and the
          back (drawn from the pieces, see views.py), what it is sewn with, the test garment note
Page 2    parts (large, all at the same scale, count badge on the part), seam allowances,
          material in two columns (fabric amounts, notions, machines and tools), the colour
          and line legend, what "left/right" means
Page 3+   the basics for the machines in use, each in a box (overlocker: allowance vs. knife
          and needle, test seam, curves, thread chain; hand stitches with a picture each;
          sewing machine: straight, zigzag, topstitching)
then      the steps, two per page: number badge, short title, tool icons with labels; left the
          picture from the real pieces, right 2–4 numbered actions, the yellow "Important" box
          and the green "Tip" box, the ×2 badge bottom right
then      "Done!" with front and back view (in the free slot of the last step page), then the
          1:1 templates (with a 5 × 5 cm control square) for every line transferred after cutting

Everything is drawn with matplotlib (vector output via PdfPages, DejaVu Sans). Every text is
wrapped to the width it really has (measured), so nothing leaves its panel; the test hook
:data:`CHECKS` collects the panel bounding boxes; ``booklet_qa`` checks views, pictures and texts on
every build.
"""
from __future__ import annotations

import re
import textwrap

import numpy as np

import booklet_qa as QA
import diagrams as DG
import ease as E
import steps as S
import units as U
import views as V
from i18n import t as T

PAGE = (8.27, 11.69)            # A4 portrait, inches
MM_IN = 25.4
INK = DG.INK
GREY = "#777777"
LIGHT = "#e6e6e6"
STEPS_PER_PAGE = 2
NOTION_WORDS = {"elastic": "Elastic", "zip": "Zip", "velcro": "Velcro", "snap": "Snaps", "button": "Buttons",
                "drawstring": "Drawstring", "cord": "Cord", "binding": "Binding", "interfacing": "Interfacing",
                "buckle": "Buckles", "wadding": "Wadding"}
IMPORTANT = ("#fff3c4", "#d4a600")      # yellow box
TIP = ("#e3f4e1", "#2e7d32")            # green box
ALT = ("#e6eef8", "#4a6fa5")            # blue box: another way to do it
OK_GREEN, BAD_RED = "#2e7d32", "#c62828"
NAVY = "#263750"                        # number badges, bullets, ×2 badges

CHECKS: list | None = None              # tests: set to [] to collect (page, rect, bboxes) per panel


# --------------------------------------------------------------------------- text helpers

def _renderer(fig):
    return fig.canvas.get_renderer()


def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width)) if text else ""


def _fit_wrap(fig, text: str, width: float, fontsize: float, **kw) -> str:
    """Wrap text so that it is at most `width` (figure fraction) wide at this font size."""
    if not text:
        return ""
    r = _renderer(fig)
    probe = fig.text(0, 0, "abcdefghijklmnopqrstuvwxyz ABCDEFG 0123456789", fontsize=fontsize, **kw)
    cw = probe.get_window_extent(r).width / len(probe.get_text())
    probe.remove()
    max_px = width * fig.bbox.width
    chars = max(8, int(max_px / cw))
    for _ in range(40):
        wrapped = "\n".join(textwrap.wrap(text, chars, break_long_words=True)) or text
        t = fig.text(0, 0, wrapped, fontsize=fontsize, **kw)
        w = t.get_window_extent(r).width
        t.remove()
        if w <= max_px or chars <= 8:
            return wrapped
        chars -= 2
    return wrapped


def _text(fig, x, y, text, width, fontsize, **kw):
    """Draw wrapped text at (x, y) (top left); returns (artist, height as figure fraction)."""
    wrapped = _fit_wrap(fig, text, width, fontsize, **{k: v for k, v in kw.items() if k in ("fontweight",)})
    t = fig.text(x, y, wrapped, fontsize=fontsize, va="top", **kw)
    h = t.get_window_extent(_renderer(fig)).height / fig.bbox.height
    return t, h


def _header(fig, pattern, page_no: int, title: str = ""):
    fig.text(0.04, 0.975, f"{T(pattern.title)} · {T(pattern.size_label)}".strip(" ·"), fontsize=7.5, color=GREY,
             va="top")
    if title:
        fig.text(0.5, 0.975, T(title), fontsize=7.5, color=GREY, va="top", ha="center")
    fig.text(0.96, 0.018, str(page_no), fontsize=8, color=GREY, ha="right")


def _line(fig, x0, x1, y, color=LIGHT, lw=0.8):
    from matplotlib.lines import Line2D
    return Line2D([x0, x1], [y, y], transform=fig.transFigure, color=color, lw=lw)


def _box(fig, x, y, w, h, fc, ec, lw=1.0, r=0.006):
    from matplotlib.patches import FancyBboxPatch
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", transform=fig.transFigure,
                       fc=fc, ec=ec, lw=lw, zorder=-1)
    fig.add_artist(p)
    return p


def _title(fig, x, y, text, size=14):
    fig.text(x, y, T(text), fontsize=size, fontweight="bold", va="top")


# --------------------------------------------------------------------------- parts

def _pack(rings, aspect: float, gap: float, label_h: float = 0.0):
    """Shelf packing of the outlines into a box of the given width/height ratio.
    Returns offsets (to add to each ring) and the overall (w, h)."""
    dims = [(np.ptp(r[:, 0]), np.ptp(r[:, 1]) + label_h) for r in rings]
    order = sorted(range(len(rings)), key=lambda i: -dims[i][1])
    area = sum((w + gap) * (h + gap) for w, h in dims)
    best = None
    for f in np.linspace(0.6, 2.2, 17):
        max_w = max(max(w for w, _ in dims), np.sqrt(area * aspect) * f)
        offs: list = [None] * len(rings)
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


def _parts_list(fig, pattern, x0, y_top, w, h_max: float) -> float:
    """All parts at the same scale, as large as the space allows: the large parts in the first row,
    the small ones (bands, pockets) below; count badge on the part, letter and name below it.
    Returns the height used."""
    pcs = pattern.pieces
    let = DG.letters(pattern)
    rings = [DG._unfolded(pc, DG._outline(pc)) for pc in pcs]
    hs = [float(np.ptp(r[:, 1])) for r in rings]
    ws = [float(np.ptp(r[:, 0])) for r in rings]
    order = sorted(range(len(pcs)), key=lambda i: -hs[i])
    big = [i for i in order if hs[i] >= 0.45 * hs[order[0]]][:5]
    rest = [i for i in order if i not in big]
    rows = [big] + [rest[k:k + 6] for k in range(0, len(rest), 6)]
    label_in = 0.42
    gap_mm = 0.25 * max(ws)
    # inches per mm: the rows stacked fill the height, every row fits the width
    s = (h_max * PAGE[1] - len(rows) * label_in) / sum(max(hs[i] for i in r) for r in rows)
    for r in rows:
        s = min(s, w * PAGE[0] * 0.96 / (sum(ws[i] for i in r) + gap_mm * len(r)))
    y = y_top
    for r in rows:
        rh = max(hs[i] for i in r) * s / PAGE[1]
        slot = w / len(r)
        for k, i in enumerate(r):
            pc, ring = pcs[i], rings[i]
            cx = x0 + slot * (k + 0.5)
            aw, ah = ws[i] * s / PAGE[0], hs[i] * s / PAGE[1]
            ax = fig.add_axes((cx - aw / 2, y - rh + (rh - ah) / 2, aw, ah))
            DG._fill(ax, ring, pc=pc)
            ax.set_xlim(ring[:, 0].min(), ring[:, 0].max())
            ax.set_ylim(ring[:, 1].min(), ring[:, 1].max())
            ax.set_aspect("auto")
            ax.axis("off")
            ax.set_clip_on(False)
            for art in ax.get_children():
                art.set_clip_on(False)
            c = (ring.min(0) + ring.max(0)) / 2
            ax.text(c[0], ring[:, 1].min() + hs[i] * 0.55, f"{pc.cut_count}×", fontsize=8.5, fontweight="bold",
                    color="white", ha="center", va="center", zorder=12, clip_on=False,
                    bbox=dict(boxstyle="round,pad=0.3", fc=NAVY, ec="none"))
            name = f"{let[pc.key]} · {T(pc.name)}" + (" (" + T("cut on fold") + ")" if pc.on_fold else "")
            fig.text(cx, y - rh - 0.006, _fit_wrap(fig, name, slot * 0.95, 7), fontsize=7, ha="center",
                     va="top", color="#333", multialignment="center")
        y -= rh + label_in / PAGE[1]
    return y_top - y


def _fabric_swatch(fig, x, y, s, pc_or_key, pattern, wrong=False):
    ax = fig.add_axes((x, y, s, s * PAGE[0] / PAGE[1]))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    sq = np.array([[0.05, 0.1], [0.95, 0.1], [0.95, 0.9], [0.05, 0.9]])
    if isinstance(pc_or_key, str):
        right, back, tex = DG.PALETTES[pc_or_key]
        if wrong:
            ax.fill(sq[:, 0], sq[:, 1], fc=back, ec=INK, lw=0.9, hatch="////", **DG._hatch_kw())
        else:
            ax.fill(sq[:, 0], sq[:, 1], fc=right, ec=INK, lw=0.9)
            if tex:
                ax.fill(sq[:, 0], sq[:, 1], fc="none", ec="none", hatch={"wale": "||", "pile": "...",
                                                                       "rib": "||"}[tex], **DG._hatch_kw())
    else:
        DG._fill(ax, sq, wrong=wrong, pc=pc_or_key)
    return ax


def _materials(pattern, plans, steps) -> list[tuple[str, str, str]]:
    """(icon key, bold name, one line of detail) for fabric, notions, machines and tools."""
    u = U.of(pattern)
    out = []
    for fab, pl in (plans or {}).items():
        import layout as L
        key = DG.palette_key(next((p for p in pattern.pieces if L.fabric_group(p) == fab), None), pattern)
        out.append(("fabric:" + key, T(fab),
                    T(f"{U.fabric_length(pl['need_mm'], u)} at {U.fabric_width(pl['width'], u)} width")))
    for en, n in zip(getattr(pattern, "notes_en", pattern.notes), pattern.notes):
        low = en.lower()
        hits = sorted((low.index(w), w) for w in NOTION_WORDS if w in low)    # the word the note starts with
        word = hits[0][1] if hits else None
        if word:
            out.append(("safety_pin" if word in ("elastic", "drawstring", "cord") else "pins",
                        T(NOTION_WORDS[word]), T(n)))
    own = S.owned_machines(pattern.options) or set()
    for t in S.machines_needed(steps, pattern.options):
        out.append((t["machine"], T(t["name"]), _tool_detail(steps, pattern, t["machine"])))
    out.append(("hand" if "hand" in own else "sewing", T("Polyester sewing thread"),
                T("In the colour of the fabric; overlocker: 4 cones.") if "overlocker" in own else
                T("In the colour of the fabric.")))
    used = {t["machine"] for t in S.machines_needed(steps, pattern.options)}
    if any("clear elastic" in st.hint for st in steps):
        out.append(("tape", T("Clear elastic or twill tape"), T("Sewn into the shoulder seams, so they do not "
                                                                "stretch out.")))
    if "overlocker" in used:
        out.append(("hand", T("Darning needle"), T("To thread the thread chains back under the overlock "
                                                   "stitches.")))
    out.append(("clips", T("Pins or clips"),
                T("Clips are safer at the overlocker: pins must come out before the knife.")
                if "overlocker" in own else T("Pin across the seam line.")))
    out.append(("chalk", T("Chalk or a fabric pen"), T("For notches, labels and placement lines.")))
    if any(s.data.get("picture") == "elastic" for s in steps) and not any(i[0] == "safety_pin" for i in out):
        out.append(("safety_pin", T("Safety pin"), T("To thread the elastic.")))
    if not any(i[0] == "iron" for i in out):
        out.append(("iron", T("Iron"), T("Steam.")))
    if E.has_nap(pattern.options):
        out.append(("towel", T("Terry towel"), T("Press from the wrong side only, on the towel.")))
    return out


def _material_grid(fig, items, pattern, x, y, w, row_h=0.043) -> float:
    """Two columns: icon, bold name, grey detail. Returns the height used."""
    col = w / 2
    for i, (icon, name, detail) in enumerate(items):
        cx = x + (i % 2) * col
        cy = y - (i // 2) * row_h
        if icon.startswith("fabric:"):
            _fabric_swatch(fig, cx + 0.004, cy - 0.027, 0.032, icon.split(":", 1)[1], pattern)
        else:
            ax = fig.add_axes((cx, cy - 0.03, 0.042, 0.03))
            DG.draw_machine(ax, icon)
        _, h1 = _text(fig, cx + 0.055, cy, name, col - 0.07, 8, fontweight="bold")
        if detail:
            _text(fig, cx + 0.055, cy - h1 - 0.002, detail, col - 0.07, 6.4, color="#555")
    return int(np.ceil(len(items) / 2)) * row_h


def _legend(fig, pattern, x, y, w) -> float:
    """Colour and line legend: fabrics (right/wrong side) and the line types. Returns height used."""
    keys = []
    for pc in pattern.pieces:
        k = DG.palette_key(pc, pattern)
        if k not in keys:
            keys.append(k)
    names = {"main": "Main fabric", "corduroy": "Corduroy", "velvet": "Velvet", "lining": "Lining",
             "rib": "Rib knit", "mesh": "Mesh"}
    col = w / 3
    y0 = y
    for i, k in enumerate(keys):
        cx = x + (i % 3) * col
        cy = y - (i // 3) * 0.04
        _fabric_swatch(fig, cx, cy - 0.022, 0.03, k, pattern)
        _fabric_swatch(fig, cx + 0.034, cy - 0.022, 0.03, k, pattern, wrong=True)
        fig.text(cx + 0.072, cy - 0.006, T(names.get(k, k)), fontsize=7.5, fontweight="bold", va="center")
        fig.text(cx + 0.072, cy - 0.019, T("right side · wrong side"), fontsize=6.3, va="center", color="#555")
    y -= 0.04 * int(np.ceil(len(keys) / 3)) + 0.01
    items = [("Sew now (machine)", dict(color=DG.STITCH, lw=1.8, ls="-")),
             ("Sew by hand", dict(color=DG.STITCH, lw=2.0, ls=DG.HAND_STITCH)),
             ("Already sewn", dict(color=DG.DONE_STITCH, lw=1.4, ls=DG.DONE_LS)),
             ("Fold / press line", dict(color=DG.ACCENT[1], lw=1.2, ls=DG.FOLD_LINE)),
             ("Marking (chalk)", "chalk"),
             ("Pin", "pin"),
             ("Notch: match them", "notch")]
    for i, (lab, kind) in enumerate(items):
        cx = x + (i % 3) * col
        cy = y - (i // 3) * 0.03
        ax = fig.add_axes((cx, cy - 0.01, 0.06, 0.02))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        if kind == "chalk":
            DG._chalk(ax, [[0.0, 0.5], [1.0, 0.5]])
        elif kind == "pin":
            ax.plot([0.15, 0.75], [0.5, 0.5], color=DG.PIN, lw=1.2)
            ax.plot([0.8], [0.5], "o", ms=4, color=DG.PIN_HEAD)
        elif kind == "notch":
            ax.plot([0.5, 0.5], [0.0, 1.0], color=INK, lw=1.4)
        else:
            ax.plot([0.0, 1.0], [0.5, 0.5], **kind)
        fig.text(cx + 0.068, cy, T(lab), fontsize=7, va="center")
    y -= 0.03 * int(np.ceil(len(items) / 3))
    return y0 - y


def difficulty(pattern, steps) -> tuple[str, float]:
    """(level, hours): a rough estimate from the number of steps and the tricky parts."""
    n = len(steps)
    tricky = sum(1 for s in steps if s.stitch in ("zip",) or s.data.get("fly") or s.diagram == "gather")
    score = n + 4 * tricky
    level = "easy" if score <= 15 else "medium" if score <= 26 else "advanced"
    hours = 0.5 + n * 0.12 + (0.3 if E.has_nap(pattern.options) else 0.0)
    return level, max(1.0, round(hours * 2) / 2)


def _key_data(pattern, steps, plans) -> list[tuple[str, str]]:
    u = U.of(pattern)
    rows = [("Size", T(pattern.size_label))]
    for fab, pl in (plans or {}).items():
        rows.append((T(fab), T(f"{U.fabric_length(pl['need_mm'], u)} at {U.fabric_width(pl['width'], u)} width")))
    notions = [name for icon, name, _d in _materials(pattern, plans, steps) if icon in ("safety_pin", "pins")]
    if notions:
        rows.append(("Notions", ", ".join(dict.fromkeys(notions))))
    machines = [t for t in S.machines_needed(steps, pattern.options)
                if t["machine"] in ("sewing", "overlocker", "coverstitch", "hand")]
    rows.append(("Sewn with", " + ".join(T(t["name"]) for t in machines) or T("Sewing machine")))
    rows.append(("Seam allowance", _sa_summary(pattern)))
    level, hours = difficulty(pattern, steps)
    rows.append(("Parts and steps", T(f"{len(pattern.pieces)} part{'s' if len(pattern.pieces) != 1 else ''} · {len(steps)} steps")))
    rows.append(("Difficulty", T(level) + " · " + T(f"about {hours:g} h")))
    return rows


def _sa_summary(pattern) -> str:
    """The seam allowances of the pieces in one line: the common one, every edge that differs
    (neckline, casing, front edge …) and the turned-up hems."""
    import allowance as A
    u = U.of(pattern)
    if not A.has_allowance(pattern):
        return T("none: add it when you cut (see the parts table)")
    sa = _common_sa(pattern)
    others: dict[str, float] = {}
    hems: set[float] = set()
    for pc in pattern.pieces:
        for e in pc.edges:
            if e.sa <= 0 or e.fold:
                continue
            v = round(e.sa, 1)
            if e.turned:
                hems.add(v)
            elif v != sa:
                lab = T(e.label or e.name).split(" (")[0]
                others.setdefault(lab, v)
    parts = [U.allowance(sa, u)]
    parts += [f"{lab} {U.allowance(v, u)}" for lab, v in sorted(others.items())]
    if hems:
        parts.append(T("turned-up hems") + " " + ", ".join(U.allowance(h, u) for h in sorted(hems)))
    return " · ".join(parts)


def _sewn_with(pattern, steps) -> list[tuple[str, str]]:
    """(icon, name) of the machines and the main tools, for the cover."""
    out = [(t["machine"], T(t["name"])) for t in S.machines_needed(steps, pattern.options)
           if t["machine"] in ("sewing", "overlocker", "coverstitch", "hand")] or [("sewing", T("Sewing machine"))]
    out.append(("iron", T("Iron")))
    if E.has_nap(pattern.options):
        out.append(("towel", T("Terry towel")))
    return out


def cover(pdf, pattern, steps, plans=None):
    """Title page: name, size and fabric in one line, the finished garment from the front and the
    back, what it is sewn with, the note about the test garment."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=PAGE)
    _header(fig, pattern, 1)
    title = T(pattern.title)
    fig.text(0.5, 0.93, title, fontsize=min(40.0, 40.0 * 16 / max(len(title), 1)), fontweight="bold",
             ha="center", va="top")
    o = pattern.options
    mod = _module(pattern)
    has_fit = mod is None or "fit" in getattr(mod, "DEFAULTS", {"fit": None})
    fit = E.describe(o.get("fit", "normal") if has_fit else None, o.get("fabric", "jersey"), o.get("stretch"))
    sub = "  ·  ".join([T(pattern.size_label), fit])
    fig.text(0.5, 0.862, _fit_wrap(fig, sub, 0.84, 10), fontsize=10, ha="center", va="top", color="#555",
             multialignment="center")
    level, hours = difficulty(pattern, steps)
    fig.text(0.5, 0.835, T(f"{len(pattern.pieces)} part{'s' if len(pattern.pieces) != 1 else ''} · {len(steps)} steps") + "  ·  " + T(level) + "  ·  "
             + T(f"about {hours:g} h"), fontsize=8, ha="center", va="top", color=GREY)
    _views(fig, pattern, (0.06, 0.29, 0.88, 0.52), check=True)
    # what it is sewn with
    tools = _sewn_with(pattern, steps)
    machines = [n for k, n in tools if k in ("sewing", "overlocker", "coverstitch", "hand")]
    _box(fig, 0.1, 0.105, 0.8, 0.15, "#f4f5f8", "#d5d9e2", lw=0.9, r=0.01)
    fig.text(0.5, 0.24, T("Sewn with") + ": " + " + ".join(machines), fontsize=10.5, fontweight="bold",
             ha="center", va="top")
    n = len(tools)
    slot = 0.8 / max(n, 1)
    for i, (key, name) in enumerate(tools):
        cx = 0.1 + slot * (i + 0.5)
        ax = fig.add_axes((cx - 0.03, 0.14, 0.06, 0.06 * PAGE[0] / PAGE[1] * 1.3))
        DG.draw_machine(ax, key)
        fig.text(cx, 0.133, _fit_wrap(fig, name, slot * 0.95, 7), fontsize=7, ha="center", va="top", color="#444",
                 multialignment="center")
    fig.text(0.5, 0.085, _fit_wrap(fig, T("Read the steps once before you start. Every picture is drawn from your "
             "pattern pieces. Sew a test garment from cheap fabric first and adjust before you cut the good "
             "fabric."), 0.8, 7.5), fontsize=7.5, color=GREY, ha="center", va="top", multialignment="center")
    pdf.savefig(fig)
    plt.close(fig)


def _views(fig, pattern, rect, captions=True, check=False):
    """Finished garment from the front and the back, side by side."""
    views = V.garment_views(pattern)
    if check:
        QA.check_views(pattern, views)
    if not views:
        ax = fig.add_axes(rect)
        rings = [DG._unfolded(pc, DG._outline(pc)) for pc in pattern.pieces]
        offs, _ = _pack(rings, rect[2] * PAGE[0] / (rect[3] * PAGE[1]), max(max(np.ptp(r, 0)) for r in rings) * 0.1)
        for pc, r, off in zip(pattern.pieces, rings, offs):
            DG._fill(ax, r + off, pc=pc)
        DG._finish_axes(ax, [r + off for r, off in zip(rings, offs)])
        return
    x, y, w, h = rect
    n = len(views)
    axes = []
    for i, (name, view) in enumerate(views.items()):
        ax = fig.add_axes((x + i * w / n, y + (0.03 if captions else 0), w / n * 0.94, h - (0.04 if captions else 0)))
        V.draw_view(ax, pattern, view, back=name == "back")
        ax.set_anchor("S")
        axes.append(ax)
    # the same scale for both views, standing on the same line
    sx = max(np.ptp(a.get_xlim()) for a in axes)
    sy = max(np.ptp(a.get_ylim()) for a in axes)
    for a in axes:
        cx, y0 = float(np.mean(a.get_xlim())), a.get_ylim()[0]
        a.set_xlim(cx - sx / 2, cx + sx / 2)
        a.set_ylim(y0, y0 + sy)
    cap = 0.04 if captions else 0.0
    # wide garments (long sleeves): one above the other when that draws them clearly larger
    side_w, side_h = w / n * 0.94 * PAGE[0], (h - cap) * PAGE[1]
    stack_w, stack_h = w * 0.94 * PAGE[0], ((h - n * cap) / n) * PAGE[1]
    scale_side = min(side_w / sx, side_h / sy) if sx > 0 and sy > 0 else 0.0
    scale_stack = min(stack_w / sx, stack_h / sy) if sx > 0 and sy > 0 else 0.0
    places = []
    if n == 2 and scale_stack > 1.2 * scale_side:
        row_h = (h - n * cap) / n
        for i in range(n):
            y0 = y + (n - 1 - i) * (row_h + cap) + cap
            need = sy * scale_stack / PAGE[1]
            lift = max(0.0, (row_h - need) / 2)
            places.append(((x + w * 0.03, y0 + lift, w * 0.94, row_h), (x + w / 2, y0 + lift - 0.022)))
    else:
        need = sy * scale_side / PAGE[1]
        lift = max(0.0, (h - cap - need) / 2)       # centre a wide garment instead of a gap above it
        for i in range(n):
            places.append(((x + i * w / n, y + cap - 0.01 + lift, w / n * 0.94, h - cap),
                           (x + (i + 0.47) * w / n, y + 0.005 + lift)))
    for a, ((ax0, ay0, aw, ah), (tx, ty)), name in zip(axes, places, views):
        a.set_position((ax0, ay0, aw, ah))
        if captions:
            fig.text(tx, ty, T("Front view" if name == "front" else "Back view"), fontsize=9, ha="center",
                     color=GREY)


def wearer(pattern) -> str:
    """Who wears the garment: "doll", "child" or "adult" (for the texts that name them)."""
    if pattern.options.get("doll"):
        return "doll"
    return "child" if pattern.measures.get("height", 1700) < 1580 else "adult"


def _sides_note(pattern) -> str:
    """What right/wrong side and left/right (as worn) mean, with an example from this garment."""
    keys = {pc.key for pc in pattern.pieces}
    who = {"doll": "the doll", "child": "the child", "adult": "the person"}[wearer(pattern)]
    if keys & {"front", "back"} and pattern.is_pants:
        example = f": the left front leg is on the right when you look at {who}."
    elif "sleeve" in keys:
        example = f": the left sleeve is on the right when you look at {who}."
    else:
        example = "."
    return ("Right/wrong side of the fabric = the side of the fabric. Left/right (as worn) = seen from "
            f"{who} wearing it" + example)


def parts_page(pdf, pattern, steps, plans, page_no: int):
    """Parts (large, same scale), seam allowances, material in two columns, the colour legend."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=PAGE)
    _header(fig, pattern, page_no, "Parts and material")
    items = _materials(pattern, plans, steps)
    row_h = 0.046
    mat_h = int(np.ceil(len(items) / 2)) * row_h
    n_keys = len({DG.palette_key(pc, pattern) for pc in pattern.pieces})
    legend_h = 0.04 * int(np.ceil(n_keys / 3)) + 0.07
    parts_h = float(np.clip(0.94 - 0.05 - 0.03 - 0.05 - mat_h - 0.05 - legend_h - 0.06, 0.13, 0.38))
    _title(fig, 0.06, 0.945, "Parts")
    y = 0.915 - _parts_list(fig, pattern, 0.06, 0.915, 0.88, parts_h)
    _, h = _text(fig, 0.06, y, T("Seam allowance (included)") + ": " + _sa_summary(pattern), 0.88, 7.5,
                 color="#444")
    y -= h + 0.025
    _title(fig, 0.06, y, "Material")
    y -= 0.035
    y -= _material_grid(fig, items, pattern, 0.06, y, 0.88, row_h) + 0.012
    _title(fig, 0.06, y, "Colours in this booklet", 11)
    y -= 0.035
    y -= _legend(fig, pattern, 0.06, y, 0.88)
    _text(fig, 0.06, y - 0.004, T(_sides_note(pattern)), 0.88, 7, color="#444")
    pdf.savefig(fig)
    plt.close(fig)


# --------------------------------------------------------------------------- tools and basics

def _tool_detail(steps, pattern, machine) -> str:
    seen = []
    for s in steps:
        if not s.stitch:
            continue
        t = S.tool_for(pattern.options, s.stitch, s.data.get("knit"))
        if t.get("machine") == machine and t.get("stitch") and T(t["stitch"]) not in seen:
            seen.append(T(t["stitch"]))
    return "; ".join(seen)


def _common_sa(pattern) -> float:
    vals = [round(e.sa, 1) for pc in pattern.pieces for e in pc.edges if e.sa > 0 and not e.fold]
    return max(set(vals), key=vals.count) if vals else 10.0


def _basic_overlocker(fig, pattern, x, y, w) -> float:
    knit = E.fabric_info(pattern.options.get("fabric", "jersey"), pattern.options.get("stretch"))[2]
    sa = _common_sa(pattern)
    _title(fig, x, y, "Basics: the overlocker", 12)
    ax = fig.add_axes((x, y - 0.2, w * 0.45, 0.17))
    ax.set_xlim(0, 60)
    ax.set_ylim(-4, 40)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.fill([0, 46, 46, 0], [0, 0, 36, 36], fc=DG.palette(None, pattern)[0], ec=INK, lw=1)
    ax.fill([2, 48, 48, 2], [2, 2, 34, 34], fc=DG.palette(None, pattern)[1], ec=INK, lw=1, hatch="////",
            **DG._hatch_kw())
    edge, needle = 48.0, 48.0 - sa
    ax.plot([edge + 3, edge + 3], [0, 36], color="#888", lw=1, ls=(0, (2, 2)))
    ax.text(edge + 3.5, 37, T("knife"), fontsize=6.5, ha="center", va="bottom")
    ax.plot([needle, needle], [2, 34], color=DG.STITCH, lw=1.6)
    ax.text(needle, 37, T("needle"), fontsize=6.5, ha="center", va="bottom", color=DG.STITCH)
    ys = np.linspace(4, 32, 15)
    ax.plot(np.where(np.arange(15) % 2, needle, edge), ys, color=DG.STITCH, lw=0.8)
    DG._dim(ax, np.array([needle, -1.5]), np.array([edge, -1.5]), S.cm(sa), 40, side=-1.0)
    ax.text(20, 18, T("seam allowance"), fontsize=6.5, ha="center", color="#555")
    lines = [T(f"Seam allowance {S.cm(sa)}: the needle runs on the seam line, the knife trims only a sliver."),
             T("Test seam on two layers of a scrap: differential " + ("1.3 (knits, also sweat and rib)" if knit
               else "1.0") + ", stitch length 3."),
             T(_curves_line(pattern)),
             T("At the end sew a 5 cm thread chain off the fabric; thread it back under the stitches with a "
               "darning needle.")]
    yy = y - 0.035
    for i, ln in enumerate(lines, 1):
        fig.text(x + w * 0.48, yy, f"{i}", fontsize=7.5, fontweight="bold", va="top", color="white",
                 bbox=dict(boxstyle="circle,pad=0.18", fc=NAVY, ec="none"))
        _, h = _text(fig, x + w * 0.51, yy, ln, w * 0.48, 7.3)
        yy -= h + 0.008
    hb = _important(fig, x + w * 0.48, yy - 0.004, w * 0.51, T("Pull the pins or clips out before they reach "
                    "the knife: a pin in the knife breaks it."), 7.2)
    return max(0.215, y - (yy - hb - 0.01))


def _curves_line(pattern) -> str:
    import machines as MC
    c = MC.curved_parts(pattern)
    return (f"Curves ({c}): sew slowly and steer the fabric, do not pull it." if c else
            "Curves: sew slowly and steer the fabric, do not pull it.")


def _stitch_pic(ax, kind):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")
    fc, bc, _ = DG.palette(None, DG._CTX["pattern"])
    if kind in ("tacking", "back", "straight", "zigzag", "bartack"):
        ax.fill([0.3, 9.7, 9.7, 0.3], [0.6, 0.6, 3.4, 3.4], fc=fc, ec=INK, lw=0.9)
    if kind == "tacking":
        for xs in range(1, 9, 2):
            ax.plot([xs, xs + 1.3], [2, 2], color=DG.STITCH, lw=1.8, solid_capstyle="round")
    elif kind == "back":
        for xs in np.arange(1.0, 8.6, 1.2):
            ax.plot([xs, xs + 1.1], [2, 2], color=DG.STITCH, lw=1.8, solid_capstyle="round")
        DG._arrow(ax, [8.6, 1.2], [6.2, 1.2], color=INK, lw=1, head=6, rad=-0.4)
    elif kind == "blind":
        ax.fill([0.3, 9.7, 9.7, 0.3], [0.4, 0.4, 3.6, 3.6], fc=bc, ec=INK, lw=0.9, hatch="////", **DG._hatch_kw())
        ax.fill([0.3, 9.7, 9.7, 0.3], [0.4, 0.4, 1.9, 1.9], fc=bc, ec=INK, lw=0.9)
        xs = np.linspace(1, 9, 9)
        ax.plot(xs, np.where(np.arange(9) % 2, 2.15, 1.75), color=DG.STITCH, lw=1.1)
    elif kind == "bartack":
        for d in np.linspace(-0.15, 0.15, 4):
            ax.plot([3, 7], [2 + d, 2 + d], color=DG.STITCH, lw=0.9)
        for xs in np.linspace(3, 7, 16):
            ax.plot([xs, xs + 0.1], [1.6, 2.4], color=DG.STITCH, lw=0.9)
    elif kind == "ladder":
        ax.fill([0.3, 4.6, 4.6, 0.3], [0.6, 0.6, 3.4, 3.4], fc=fc, ec=INK, lw=0.9)
        ax.fill([5.4, 9.7, 9.7, 5.4], [0.6, 0.6, 3.4, 3.4], fc=fc, ec=INK, lw=0.9)
        for yy in np.linspace(1, 3, 6):
            ax.plot([4.6, 5.4], [yy, yy], color=DG.STITCH, lw=1.2)
    elif kind == "straight":
        ax.plot([0.8, 9.2], [2, 2], color=DG.STITCH, lw=1.8)
    elif kind == "zigzag":
        xs = np.linspace(0.8, 9.2, 19)
        ax.plot(xs, np.where(np.arange(19) % 2, 2.5, 1.5), color=DG.STITCH, lw=1.2)
    elif kind in ("cover", "cover_end"):
        ax.fill([0.3, 9.7, 9.7, 0.3], [0.6, 0.6, 3.4, 3.4], fc=fc, ec=INK, lw=0.9)
        end = 6.2 if kind == "cover_end" else 9.2
        for yy in (1.6, 2.4):
            ax.plot([0.8, end], [yy, yy], color=DG.STITCH, lw=1.5)
        if kind == "cover_end":
            ax.plot([0.8, 2.0], [1.6, 1.6], color=DG.STITCH, lw=3.0, alpha=0.5)
            ax.plot([0.8, 2.0], [2.4, 2.4], color=DG.STITCH, lw=3.0, alpha=0.5)
    elif kind == "topstitch":
        ax.fill([0.3, 9.7, 9.7, 0.3], [0.6, 0.6, 3.4, 3.4], fc=fc, ec=INK, lw=0.9)
        ax.plot([0.3, 9.7], [3.4, 3.4], color=INK, lw=2.2)
        ax.plot([0.8, 9.2], [2.7, 2.7], color=DG.STITCH, lw=1.6)


HAND_BASICS = [("tacking", "Tacking stitch", "Long running stitches (1 cm), they come out again later."),
               ("back", "Back stitch", "Each stitch goes back to the end of the last one: strong like a machine "
                "seam; for topstitching and seams."),
               ("blind", "Blind stitch", "For hems and casings: catch only 1–2 threads of the outer fabric, "
                "then 5 mm in the fold."),
               ("bartack", "Bar tack", "4–5 stitches on top of each other, then wrapped closely with "
                "buttonhole stitches."),
               ("ladder", "Ladder stitch", "Closes an opening invisibly: the stitches run inside the folds.")]
MACHINE_BASICS = [("straight", "Straight stitch", "Seams in woven fabric, 2.5 mm; backstitch at the start and "
                   "the end."),
                  ("zigzag", "Zigzag", "Knit seams (narrow) and finishing the edges (wide)."),
                  ("topstitch", "Topstitching", "Right side up, with the same distance to the edge all the way; "
                   "use the edge of the presser foot as a guide.")]


HAND_KIND = {"tacking stitch": "tacking", "back stitch": "back", "blind stitch": "blind", "hand bar tack": "bartack",
             "ladder stitch": "ladder", "box of hand stitches": "back", "2 rows of running stitch": "tacking"}


def _hand_basics(pattern, steps) -> list:
    """Only the hand stitches the steps really use (a picture and a line each)."""
    kinds = set()
    for s in steps:
        t = S.tool_for(pattern.options, s.stitch, s.data.get("knit")) if s.stitch else {}
        if s.data.get("picture") == "hand" and t.get("machine", "hand") == "hand":
            kinds.add("ladder")
        if not s.stitch:
            continue
        if t.get("machine") == "hand":
            st = str(t.get("stitch", "")).split(",")[0].strip()
            kinds.add(next((v for k, v in HAND_KIND.items() if st.startswith(k)), "back"))
    return [it for it in HAND_BASICS if it[0] in kinds]


COVER_BASICS = [("cover", "Cover stitch", "Hems and topstitching on knits: right side up, two needles on top, the "
                  "looper covers the raw edge underneath."),
                 ("cover_end", "Ending the seam", "Sew 1 cm over the start, lift the needles, pull the fabric back "
                  "and cut; knot the needle threads on the wrong side.")]


def _basic_grid(fig, title, items, x, y, w) -> float:
    _title(fig, x, y, title, 12)
    col = w / 3
    rows = int(np.ceil(len(items) / 3))
    for i, (kind, name, text) in enumerate(items):
        cx = x + (i % 3) * col
        cy = y - 0.035 - (i // 3) * 0.13
        ax = fig.add_axes((cx, cy - 0.05, col * 0.85, 0.05))
        _stitch_pic(ax, kind)
        fig.text(cx, cy - 0.057, T(name), fontsize=8.5, fontweight="bold", va="top")
        _text(fig, cx, cy - 0.073, T(text), col * 0.92, 6.6, color="#444")
    return 0.04 + rows * 0.13


def tools_pages(pdf, pattern, steps, page_no: int) -> int:
    """The basics for the machines the steps use, each in its own box (overlocker: allowance vs.
    knife and needle; hand stitches with a picture each; sewing machine)."""
    import matplotlib.pyplot as plt
    tools = S.machines_needed(steps, pattern.options)
    used = {t["machine"] for t in tools}
    names = [T(t["name"]) for t in tools if t["machine"] in ("sewing", "overlocker", "coverstitch", "hand")]
    fig = plt.figure(figsize=PAGE)
    _header(fig, pattern, page_no, "Basics")
    _title(fig, 0.06, 0.945, T("Basics") + ": " + (" " + T("and") + " ").join(names or [T("Sewing machine")]))
    y = 0.905
    if S.owned_machines(pattern.options) is None:
        _, h = _text(fig, 0.06, y, T("Steps are written for a sewing machine with zigzag. Have an overlocker or a "
                     "coverstitch machine? Tell the generator which machines you own and the steps use them."),
                     0.88, 7, color=GREY)
        y -= h + 0.015
    blocks = []
    if "overlocker" in used:
        blocks.append(("overlocker", 0.24))
    hand_items = _hand_basics(pattern, steps)
    if hand_items:
        blocks.append(("hand", 0.04 + int(np.ceil(len(hand_items) / 3)) * 0.13))
    if "sewing" in used or not blocks:
        blocks.append(("sewing", 0.04 + 0.13))
    if "coverstitch" in used:
        blocks.append(("coverstitch", 0.04 + 0.13))
    for kind, h in blocks:
        if y - h - 0.03 < 0.04:
            pdf.savefig(fig)
            plt.close(fig)
            page_no += 1
            fig = plt.figure(figsize=PAGE)
            _header(fig, pattern, page_no, "Basics")
            y = 0.945
        top = y
        y -= 0.018
        if kind == "overlocker":
            used_h = _basic_overlocker(fig, pattern, 0.08, y, 0.84)
        elif kind == "hand":
            used_h = _basic_grid(fig, "Basics: hand stitches", hand_items, 0.08, y, 0.84)
        elif kind == "coverstitch":
            used_h = _basic_grid(fig, "Basics: the coverstitch machine", COVER_BASICS, 0.08, y, 0.84)
        else:
            used_h = _basic_grid(fig, "Basics: the sewing machine", MACHINE_BASICS, 0.08, y, 0.84)
        y -= used_h + 0.01
        _box(fig, 0.06, y, 0.88, top - y, "none", "#d5d9e2", lw=0.9, r=0.01)
        y -= 0.02
    pdf.savefig(fig)
    plt.close(fig)
    return page_no + 1


# --------------------------------------------------------------------------- steps

def _actions(text: str) -> list[str]:
    """Split a step text into 1–4 short numbered actions."""
    if not text:
        return []
    parts = [p.strip(" ;") for p in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9„\"])|;\s+", text) if p.strip(" ;")]
    while len(parts) > 5:
        i = min(range(len(parts) - 1), key=lambda k: len(parts[k]) + len(parts[k + 1]))
        parts[i:i + 2] = [parts[i].rstrip(".") + "; " + parts[i + 1][:1].lower() + parts[i + 1][1:]]
    return [p[:1].upper() + p[1:] for p in parts]


def _important(fig, x, y, w, text, fs, label="Important", colors=IMPORTANT, icon="⚠") -> float:
    """Yellow (or green) box: one paragraph that starts with the label ("⚠ Important: …"); returns its height."""
    pad = 0.006
    head = (f"{icon} " if icon else "") + T(label) + ": "
    _, h2 = _text(fig, x + pad, y - pad, head + text, w - 2 * pad, fs, color="#333")
    h = h2 + 2 * pad
    p = _box(fig, x, y - h, w, h, colors[0], colors[1], lw=0.8)
    p.set_zorder(-1)
    return h


def _step_tools(pattern, step) -> list[tuple[str, str]]:
    """(icon key, label) of the tools a step uses."""
    out = []
    if step.stitch:
        t = S.tool_for(pattern.options, step.stitch, step.data.get("knit"))
        if t:
            out.append((t["machine"], t["name"]))
    if step.diagram == "seam" or step.stitch in ("seam", "band"):
        own = S.owned_machines(pattern.options) or set()
        out.append(("clips" if "overlocker" in own else "pins", "Clips" if "overlocker" in own else "Pins"))
    if step.data.get("picture") == "elastic":
        out.append(("safety_pin", "Safety pin"))
    if step.data.get("picture") == "cut":
        out.append(("scissors", "Scissors"))
    if step.diagram == "label" or step.data.get("picture") == "notch":
        out.append(("chalk", "Chalk"))
    if step.data.get("press_check"):
        out += [("iron", "Iron"), ("towel", "Terry towel")]
    seen, res = set(), []
    for k, lab in out:
        if k not in seen:
            seen.add(k)
            res.append((k, lab))
    return res[:3]


def _check_pair(fig, pattern, step, rect):
    """✓ / ✗ pictures where a mix-up is likely: the single back pocket, pressing a fabric with nap."""
    x, y, w, h = rect
    if step.data.get("only"):
        side = step.data["only"]
        back = pattern.piece("back")
        ring = DG._outline(back)
        mark = next((m for m in back.marks if (getattr(m, "key", None) or m.label).startswith("Back pocket")), None)
        for i, good_side in enumerate((side, "left" if side == "right" else "right")):
            ax = fig.add_axes((x + i * w / 2, y, w / 2 * 0.8, h))
            mirrored = good_side == "left"
            r = DG._mirror_x(ring, 0.0) if mirrored else ring
            DG._fill(ax, r, pc=back)
            if mark is not None:
                mp = np.asarray(mark.pts, float)
                mp = DG._mirror_x(mp, 0.0) if mirrored else mp
                ax.fill(mp[:, 0], mp[:, 1], fc="white" if i == 0 else "#ffcdd2", ec=INK, lw=0.8, zorder=3)
            c = (r.min(0) + r.max(0)) / 2
            DG._tag(ax, (c[0], c[1] - np.ptp(r[:, 1]) * 0.15), T("BL" if mirrored else "BR"), size=7)
            DG._finish_axes(ax, [r], pad=0.04)
            fig.text(x + i * w / 2 + w / 2 * 0.82, y + h * 0.55, "✓" if i == 0 else "✗", fontsize=18,
                     fontweight="bold", color=OK_GREEN if i == 0 else BAD_RED, ha="left", va="center")
    elif step.data.get("press_check"):
        for i in range(2):
            ax = fig.add_axes((x + i * w / 2, y, w / 2 * 0.78, h))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.fill([0.5, 9.5, 9.5, 0.5], [0.4, 0.4, 2.2, 2.2], fc="#e1f5fe", ec=INK, lw=0.8)
            sq = np.array([[1.5, 1.4], [8.5, 1.4], [8.5, 3.2], [1.5, 3.2]])
            DG._fill(ax, sq, wrong=i == 0, z=2, pc=pattern.pieces[0])
            iax = ax.inset_axes((0.3, 0.5, 0.4, 0.5))
            DG.draw_machine(iax, "iron")
            fig.text(x + i * w / 2 + w / 2 * 0.8, y + h * 0.55, "✓" if i == 0 else "✗", fontsize=18,
                     fontweight="bold", color=OK_GREEN if i == 0 else BAD_RED, ha="left", va="center")
            _text(fig, x + i * w / 2, y - 0.002, T("wrong side up on a towel" if i == 0 else
                                                   "right side up: the pile goes flat"), w / 2 * 0.95, 6.3,
                  color="#444")


def _panel(fig, pattern, n: int, step: S.Step, rect, prev_section: str):
    x, y, w, h = rect
    _box(fig, x, y, w, h, "none", LIGHT, lw=0.9)
    first = len(fig.texts)
    # header: number badge, section, title, ×2, tools
    fig.text(x + 0.03, y + h - 0.032, str(n), fontsize=14 if n < 100 else 11, fontweight="bold", color="white",
             ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.38", fc=NAVY, ec="none"))
    tools = _step_tools(pattern, step)
    tools_w = 0.075 * len(tools)
    title_w = w - 0.075 - tools_w - 0.02
    _text(fig, x + 0.065, y + h - 0.024, T(step.title), title_w, 11.5, fontweight="bold")
    tx = x + w - 0.012 - tools_w
    for i, (key, lab) in enumerate(tools):
        iax = fig.add_axes((tx + i * 0.075 + 0.017, y + h - 0.047, 0.04, 0.04 * PAGE[0] / PAGE[1] * 1.3))
        DG.draw_machine(iax, key)
        fig.text(tx + i * 0.075 + 0.037, y + h - 0.05, _fit_wrap(fig, T(lab), 0.072, 5.8), fontsize=5.8,
                 ha="center", va="top", color="#444")
    if step.repeat > 1:
        fig.text(x + w - 0.014, y + 0.012, f"{step.repeat}×", fontsize=11, fontweight="bold", ha="right",
                 va="bottom", color="white", bbox=dict(boxstyle="round,pad=0.35", fc=NAVY, ec="none"))
    head_h = 0.075
    # picture (left ≈ 60 %)
    pic_w = w * 0.58
    pic_top = y + h - head_h
    check = bool(step.data.get("only") or step.data.get("press_check"))
    pic_h = pic_top - y - 0.012
    if check:
        ch = pic_h * 0.32
        _check_pair(fig, pattern, step, (x + 0.012, y + 0.022, pic_w - 0.024, ch - 0.02))
        ax = fig.add_axes((x + 0.012, y + 0.012 + ch, pic_w - 0.024, pic_h - ch))
    else:
        ax = fig.add_axes((x + 0.012, y + 0.012, pic_w - 0.024, pic_h))
    DG.draw(ax, pattern, step)
    pos = ax.get_position()
    QA.check_picture(ax, n, T(step.title), (pos.x0, pos.y0, pos.width, pos.height))
    # instructions (right ≈ 40 %)
    cx, cw = x + pic_w + 0.01, w - pic_w - 0.022
    tool = S.tool_for(pattern.options, step.stitch, step.data.get("knit")) if step.stitch else {}
    for fs in (8.6, 8.0, 7.4, 6.8, 6.2, 5.6):
        mark = len(fig.texts), len(fig.patches), len(fig.artists)
        yy = pic_top - 0.004
        for i, a in enumerate(_actions(T(step.text)), 1):
            fig.text(cx, yy, f"{i}", fontsize=fs, fontweight="bold", color="white", va="top",
                     bbox=dict(boxstyle="circle,pad=0.18", fc=NAVY, ec="none"))
            _, hh = _text(fig, cx + 0.022, yy, a, cw - 0.022, fs, color="#222")
            yy -= hh + 0.009
        if tool and tool.get("stitch"):
            _, hh = _text(fig, cx, yy, T(tool["name"]) + ": " + T(tool["stitch"]), cw, fs * 0.85, color=GREY)
            yy -= hh + 0.01
        if step.tip:
            yy -= _important(fig, cx, yy, cw, T(step.tip), fs * 0.92) + 0.008
        if step.hint:
            yy -= _important(fig, cx, yy, cw, T(step.hint), fs * 0.92, label="Tip", colors=TIP, icon="") + 0.008
        if step.alt:
            yy -= _important(fig, cx, yy, cw, T(step.alt), fs * 0.92, label="Alternative", colors=ALT,
                             icon="") + 0.008
        if yy >= y + (0.045 if step.repeat > 1 else 0.008):
            break
        # too long: remove what this pass drew and try a smaller size
        for t in list(fig.texts[mark[0]:]):
            t.remove()
        for art in list(fig.artists[mark[2]:]):
            art.remove()
    return dict(step=n, rect=rect, fig=fig, texts=fig.texts[first:], axes=None)


def step_pages(pdf, pattern, steps, first_page: int) -> int:
    """Two steps per page; with an odd number of steps the "Done!" panel fills the last slot."""
    import matplotlib.pyplot as plt
    page = first_page
    prev = ""
    mx, top, bottom, gap = 0.04, 0.955, 0.04, 0.014
    ph = (top - bottom - gap) / STEPS_PER_PAGE
    for start in range(0, len(steps), STEPS_PER_PAGE):
        fig = plt.figure(figsize=PAGE)
        _header(fig, pattern, page)
        chunk = steps[start:start + STEPS_PER_PAGE]
        for k, st in enumerate(chunk):
            rect = (mx, top - (k + 1) * ph - k * gap, 1 - 2 * mx, ph)
            before = len(fig.axes)
            rec = _panel(fig, pattern, start + k + 1, st, rect, prev)
            rec["axes"] = fig.axes[before:]
            rec["page"] = page
            _measure(rec)
            QA.check_panel_text(rec)
            if CHECKS is not None:
                CHECKS.append(rec)
            prev = st.section
        if len(chunk) < STEPS_PER_PAGE:
            k = len(chunk)
            _done_panel(fig, pattern, steps, (mx, top - (k + 1) * ph - k * gap, 1 - 2 * mx, ph))
        pdf.savefig(fig)
        plt.close(fig)
        page += 1
    return page


def _measure(rec):
    """Bounding boxes (figure fraction) of the panel's texts and axes, for the tests."""
    fig = rec["fig"]
    r = _renderer(fig)
    W, H = fig.bbox.width, fig.bbox.height
    boxes = []
    for t in rec["texts"]:
        if not t.get_text().strip():
            continue
        b = t.get_window_extent(r)
        boxes.append(("text", t.get_text()[:40], (b.x0 / W, b.y0 / H, b.x1 / W, b.y1 / H)))
    for a in rec["axes"]:
        b = a.get_position()
        boxes.append(("axes", "", (b.x0, b.y0, b.x1, b.y1)))
    rec["boxes"] = boxes
    rec.pop("fig")
    rec.pop("texts")
    rec.pop("axes")


# --------------------------------------------------------------------------- templates and done

def templates(pattern) -> list[tuple]:
    """(piece, mark) for every line that is transferred after cutting."""
    return [(pc, m) for pc in pattern.pieces for m in pc.marks if getattr(m, "template", False)]


def template_pages(pdf, pattern, page_no: int) -> int:
    """1:1 templates (true scale) with a 5 × 5 cm control square."""
    import matplotlib.pyplot as plt
    for pc, m in templates(pattern):
        fig = plt.figure(figsize=PAGE)
        _header(fig, pattern, page_no, "Templates 1:1")
        lab = T(m.label)
        _title(fig, 0.06, 0.935, T("Template") + ": " + lab)
        _text(fig, 0.06, 0.9, T("Print at 100 % and measure the control square. Cut the template out along the "
              "grey outline, lay it on the piece (right side up) with the edges on the edges, and trace the line "
              "with chalk."), 0.88, 8)
        pts = np.asarray(m.pts, float)
        pad = 25.0
        x0, y0 = pts.min(0) - pad
        x1, y1 = pts.max(0) + pad
        w_mm, h_mm = x1 - x0, y1 - y0
        left_in, bottom_in = 0.9, 1.2
        ax = fig.add_axes((left_in / PAGE[0], bottom_in / PAGE[1], w_mm / MM_IN / PAGE[0], h_mm / MM_IN / PAGE[1]))
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.axis("off")
        from shapely.geometry import Polygon, box
        clip = Polygon(np.asarray(pc.seam_ring(), float)).buffer(0).intersection(box(x0, y0, x1, y1))
        if not clip.is_empty and clip.geom_type == "Polygon":
            c = np.asarray(clip.exterior.coords)
            ax.fill(c[:, 0], c[:, 1], fc=DG.palette(pc, pattern)[0], ec="#888", lw=1.0, alpha=0.35)
        ax.plot(pts[:, 0], pts[:, 1], color=DG.STITCH, lw=1.2)
        fly = pattern.options.get("_fly") if isinstance(pattern.options, dict) else None
        if fly and m.label.lower().startswith("fake fly") or (fly and "fly" in getattr(m, "key", "").lower()):
            import geometry as G
            inner = G.offset_polyline(pts, fly["spacing"]) if hasattr(G, "offset_polyline") else pts
            ax.plot(inner[:, 0], inner[:, 1], color=DG.STITCH, lw=1.0, ls=(0, (3, 2)))
            end = pts[-1]
            ax.plot([end[0] - 4, end[0] + 4], [end[1], end[1]], color=DG.STITCH, lw=3.2)
            fig.text(0.06, 0.86, T(f"Two rows {S.cm(fly['spacing'])} apart, {S.cm(fly['offset'])} from centre "
                     f"front, {fly['length'] / 10:.1f} cm long, curve radius {S.cm(fly['radius'])}; bar tack at "
                     "the crotch seam."), fontsize=8, va="top", color="#333")
        # control square 5 × 5 cm
        sq_left = min(PAGE[0] - 0.6 - 50 / MM_IN, (left_in + w_mm / MM_IN + 0.4))
        sax = fig.add_axes((sq_left / PAGE[0], bottom_in / PAGE[1], 50 / MM_IN / PAGE[0], 50 / MM_IN / PAGE[1]))
        sax.set_xlim(0, 50)
        sax.set_ylim(0, 50)
        sax.axis("off")
        sax.fill([0, 50, 50, 0], [0, 0, 50, 50], fc="none", ec=INK, lw=1.2)
        sax.text(25, 25, "5 × 5 cm", ha="center", va="center", fontsize=9)
        pdf.savefig(fig)
        plt.close(fig)
        page_no += 1
    return page_no


def _done_panel(fig, pattern, steps, rect):
    """"Done!": the finished garment from the front and the back, and what to do after the test garment."""
    x, y, w, h = rect
    _box(fig, x, y, w, h, "none", LIGHT, lw=0.9)
    fig.text(x + w * 0.36, y + h - 0.018, T("Done!"), fontsize=24, fontweight="bold", ha="center", va="top")
    _views(fig, pattern, (x + 0.02, y + 0.012, w * 0.68, h - 0.075))
    _important(fig, x + w * 0.73, y + h * 0.62, w * 0.25, T(_fit_check(pattern)), 7.2,
               label="After the test garment", colors=TIP, icon="")


def _module(pattern):
    """The garment module of a pattern (None for unknown garments)."""
    import garments as GM
    return GM.get(pattern.garment) if pattern.garment in GM.GARMENTS else None


def _fit_check(pattern) -> str:
    """What to check on the test garment, for this kind of garment and wearer."""
    keys = {pc.key for pc in pattern.pieces}
    who = wearer(pattern)
    if who == "doll":
        return ("Try the test garment on the doll: does it go over the head, does the opening close, is the "
                "length right? Adjust the measurements and print the pattern again before you cut the good fabric.")
    on = "Try the test garment on the child" if who == "child" else "Try the test garment on"
    fit_note = getattr(_module(pattern), "FIT_CHECK", None)
    if fit_note:
        return f"{on}: {fit_note} Adjust the measurements or options and print the pattern again if needed."  # i18n: template
    if "sleeve" in keys or "hood" in keys:
        what = "length, chest width, sleeve length and the neckline"
    elif pattern.is_pants:
        what = "length, width at the hip, the crotch and the waistband"
    else:
        what = "length, width at the hip and the waistband"
    return (f"{on}: {what}. Adjust the measurements or options and print the pattern again before you cut the "
            "good fabric.")


def done_page(pdf, pattern, steps, page_no: int) -> int:
    """A page of its own for "Done!" when the last step page is full."""
    import matplotlib.pyplot as plt
    if len(steps) % STEPS_PER_PAGE:
        return page_no
    fig = plt.figure(figsize=PAGE)
    _header(fig, pattern, page_no)
    _done_panel(fig, pattern, steps, (0.04, 0.5 + 0.007, 0.92, 0.448))
    pdf.savefig(fig)
    plt.close(fig)
    return page_no + 1


def build(pattern, path: str, plans=None, steps: list[S.Step] | None = None) -> str:
    """Write the booklet PDF; returns the path."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    steps = steps if steps is not None else S.assembly(pattern)
    if steps and "done" not in steps[-1].data:
        S.annotate_progress(pattern, steps)
    DG._CTX["pattern"] = pattern
    QA.reset()
    with plt.rc_context({"font.family": "DejaVu Sans", "pdf.fonttype": 42}):
        with PdfPages(path, metadata={"Title": f"{T(pattern.title)} – " + T("sewing instructions"),
                                      "Creator": "sewing-pattern-generator"}) as pdf:
            cover(pdf, pattern, steps, plans)
            parts_page(pdf, pattern, steps, plans, 2)
            page = tools_pages(pdf, pattern, steps, 3)
            page = step_pages(pdf, pattern, steps, page)
            page = done_page(pdf, pattern, steps, page)
            template_pages(pdf, pattern, page)
    return path
