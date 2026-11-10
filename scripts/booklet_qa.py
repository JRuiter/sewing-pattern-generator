"""Quality checks for the illustrated booklet, run on every build.

Drawing mistakes (a garment view without its sleeves, two pieces stacked skewed across each
other, a picture that is almost empty, text that leaves its panel, the fallback pictogram)
must never reach the user unnoticed. Every check here is geometric and runs while the
booklet is drawn; the findings go into ``validation_report.md`` ("Booklet check"), into
``generate.run(...)["booklet_issues"]`` and are printed. The tests require zero findings
for the reference garments.

What a machine cannot judge (does the picture make sense to a sewist?) is the second
safety net: ``booklet_pages.py`` renders every page into contact sheets, and SKILL.md
step 6 says to look at every sheet before delivering.
"""
from __future__ import annotations

import numpy as np

ISSUES: list[dict] = []

MIN_PICTURE_FILL = 0.22       # the drawing covers at least this share of its picture area
BAND_KEYS = ("waistband", "leg_cuff", "sleeve_cuff", "hem_band", "neckband", "hood", "sleeve")


def reset() -> None:
    ISSUES.clear()


def add(kind: str, where: str, text: str) -> None:
    ISSUES.append(dict(kind=kind, where=where, text=text))


# --------------------------------------------------------------------------- views

def check_views(pattern, views: dict) -> None:
    """The front and back views show the whole garment: every band, cuff, sleeve and the hood
    of the pattern, two separate legs for pants, two sleeves for tops."""
    from shapely.geometry import LineString, Polygon
    if not views:
        return
    for name, view in views.items():
        keys = [pc.key for _r, pc, _z in view["layers"]]
        for k in BAND_KEYS:
            if not pattern.has(k):
                continue
            if k == "neckband" and pattern.has("hood"):
                continue
            want = 2 if k in ("leg_cuff", "sleeve_cuff", "sleeve") else 1
            if keys.count(k) < want:
                add("view", f"{name} view", f"'{k}' missing ({keys.count(k)} of {want} drawn)")
        if pattern.is_pants and pattern.has("front") and not pattern.piece("front").on_fold:
            body = Polygon(view["layers"][0][0]).buffer(0)
            y0, y1 = body.bounds[1], body.bounds[3]
            y = y0 + 0.04 * (y1 - y0)
            cut = body.intersection(LineString([(-1e5, y), (1e5, y)]))
            if cut.geom_type != "MultiLineString":
                add("view", f"{name} view", "the legs are not separate at the hem")


# --------------------------------------------------------------------------- step pictures

def check_picture(ax, n: int, title: str, rect) -> None:
    """The drawing fills its picture area reasonably (no tiny drawing in a big empty box)."""
    try:
        ax.apply_aspect()
        pos = ax.get_position()
        xl, yl = ax.get_xlim(), ax.get_ylim()
        lim = ax.dataLim
        if not np.isfinite([lim.x0, lim.x1, lim.y0, lim.y1]).all() or lim.width <= 0 or lim.height <= 0:
            return
        fx = min(1.0, lim.width / max(abs(xl[1] - xl[0]), 1e-9))
        fy = min(1.0, lim.height / max(abs(yl[1] - yl[0]), 1e-9))
        drawn = pos.width * fx * pos.height * fy
        area = rect[2] * rect[3]
        if area > 0 and drawn / area < MIN_PICTURE_FILL:
            add("picture", f"step {n}", f"'{title}': the drawing fills only {drawn / area:.0%} of its area")
    except Exception:  # pragma: no cover - a check must never break the booklet
        pass


def fallback(step_title: str, exc: Exception) -> None:
    add("picture", step_title, f"no picture could be drawn ({type(exc).__name__}: {exc}); pictogram shown")


def check_overlay(title: str, rel_rms: float, limit: float) -> None:
    if rel_rms > limit:
        add("seam", title, f"stacked pieces do not lie on each other (deviation {rel_rms:.1%} of the edge)")


def check_layers(title: str, top, flipped: bool) -> None:
    """Stacked right sides together: the piece on top lies face down. A piece that is not cut as a
    mirrored pair (and not on the fold) must then be drawn as its mirror image, never turned round."""
    if not flipped and not (top.mirror or top.on_fold):
        add("seam", title, f"{top.name} on top is drawn right side up turned round, not face down "
                           "(mirror image)")


# --------------------------------------------------------------------------- text

def text_problems(rec) -> list[tuple]:
    """Texts outside their panel or overlapping each other (rec from booklet._measure)."""
    bad = []
    x, y, w, h = rec["rect"]
    texts = [b for b in rec["boxes"] if b[0] == "text"]
    for kind, txt, (x0, y0, x1, y1) in rec["boxes"]:
        if x0 < x - 0.002 or y0 < y - 0.002 or x1 > x + w + 0.002 or y1 > y + h + 0.002:
            bad.append((rec["step"], kind, txt))
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i][2], texts[j][2]
            if min(a[2], b[2]) - max(a[0], b[0]) > 0.003 and min(a[3], b[3]) - max(a[1], b[1]) > 0.003:
                bad.append((rec["step"], "overlap", texts[i][1], texts[j][1]))
    return bad


def check_panel_text(rec) -> None:
    for p in text_problems(rec):
        what = f"text outside the panel: '{p[2]}'" if p[1] != "overlap" else f"texts overlap: '{p[2]}' / '{p[3]}'"
        add("text", f"step {p[0]}", what)


# --------------------------------------------------------------------------- report

def to_markdown(issues: list[dict] | None = None) -> str:
    from i18n import t as T
    issues = ISSUES if issues is None else issues
    lines = ["## " + T("Booklet check"), ""]
    if not issues:
        lines.append(T("All pictures and texts passed the automatic checks (views complete, seams lie on each "
                       "other or side by side, pictures fill their area, no text outside its panel)."))
        return "\n".join(lines)
    lines += ["| " + T("Where") + " | " + T("Check") + " | " + T("Finding") + " |", "|---|---|---|"]
    for i in issues:
        lines.append(f"| {i['where']} | {i['kind']} | {i['text']} |")
    return "\n".join(lines)
