"""Step diagrams for the sewing instructions (issue #10).

Every sewing step that closes a seam of the seam graph (`Pattern.seams`) gets a small
diagram drawn from the real pattern geometry: the pieces involved (seam line, right side
shaded), the edges to sew highlighted in one colour per seam, and the matching notches.
The only garment-specific part is the step → seam mapping in `STEP_SEAMS` (a module can
add its own rules as `STEP_SEAMS` in the module); everything else is generic, so the
diagrams stay correct for every size and option.
"""
from __future__ import annotations

import os

import numpy as np

import geometry as G

# (text that identifies the step, seam name prefixes). First matching rule wins; a rule
# with no prefixes means "no seam of the graph is sewn here" (e.g. closing a band into a ring).
STEP_SEAMS: list[tuple[str, list[str]]] = [
    ("**Side pockets:**", ["Pocket opening"]),
    ("Place the side panel right sides together under the pocket bag", ["Pocket bag"]),
    ("**Side and sleeve seams:**", ["Side seam", "Sleeve seam"]),
    ("**Skirt side seams:**", ["Skirt side seam"]),
    ("**Side seams:**", ["Side seam"]),
    ("**Inseams:**", ["Inseam"]),
    ("**Crotch seam:**", ["Front crotch seam", "Back crotch seam"]),
    ("Divide waistband and pants top edge", ["Waistband"]),
    ("Sew the waistband to the pants top edge", ["Waistband"]),
    ("sew to the skirt", ["Waistband"]),
    ("**Waistband:**", []),
    ("Slip the cuff over", ["Leg cuff"]),
    ("**Leg cuffs:**", []),
    ("**Shoulders:**", ["Shoulder seam"]),
    ("**Neckband:**", ["Neckband"]),
    ("**Set in the sleeves:**", ["Armhole"]),
    ("**Raglan seams:**", ["Raglan seam"]),
    ("**Sleeve cuffs:**", ["Sleeve cuff"]),
    ("**Hem band:**", ["Hem band"]),
    ("**Hood:**", ["Hood centre seam"]),
    ("**Attach the hood:**", ["Hood ↔"]),
    ("**Zip:**", ["Zip"]),
    ("**Waist seam:**", ["Waist seam"]),
    ("**Beanie:**", ["Side seams", "Crown seam"]),
    ("**Brim:**", ["Brim"]),
    ("**Long seam:**", ["Long edges"]),
    ("**Turn:**", ["Cross seam"]),
]

COLORS = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd"]
RIGHT_SIDE = "#f3d9a4"
WRONG_SIDE = "#ffffff"


def _rules(pattern):
    try:
        from garments import get
        extra = list(getattr(get(pattern.garment), "STEP_SEAMS", []) or [])
    except Exception:  # pragma: no cover
        extra = []
    return extra + STEP_SEAMS


def step_seams(pattern, steps: list[str]) -> list[list[dict]]:
    """For each step the seams (entries of pattern.seams) it sews; [] = no diagram."""
    rules = _rules(pattern)
    out = []
    for s in steps:
        found: list[dict] = []
        for key, prefixes in rules:
            if key in s:
                found = [sm for sm in pattern.seams if any(sm["name"].startswith(p) for p in prefixes)]
                break
        out.append(found)
    return out


def _notch_points(pc, edge_name):
    e = pc.edge(edge_name)
    L = e.length
    pts = []
    for n in pc.notches:
        if n.edge != edge_name:
            continue
        s = n.s if n.s >= 0 else L + n.s
        if 0 <= s <= L:
            pts.append((G.point_at(e.pts, s), G.tangent_at(e.pts, s), n.count))
    return pts


def _instances(pattern, seams):
    """Pieces to draw: (piece key, mirrored?). A seam joining an edge to the same edge of the
    same piece (crotch seam, hood centre, zip) joins the left and the right piece: draw both."""
    inst: list[tuple[str, bool]] = []
    for sm in seams:
        a = {(p, e) for p, e, _ in sm["a"]}
        b = {(p, e) for p, e, _ in sm["b"]}
        for p, _e, _n in sm["a"] + sm["b"]:
            if (p, False) not in inst:
                inst.append((p, False))
        for p, _e in a & b:
            if (p, True) not in inst:
                inst.append((p, True))
    return inst


def _arrange(rings, gap):
    """Simple shelf packing: rows of pieces, row width ≈ 2.4 × the largest piece height."""
    hs = [np.ptp(r[:, 1]) for r in rings]
    ws = [np.ptp(r[:, 0]) for r in rings]
    max_w = max(sum(ws) / 2 + gap, max(ws), 2.4 * max(hs))
    offs, x, y, row_h = [], 0.0, 0.0, 0.0
    for w, h in zip(ws, hs):
        if x > 0 and x + w > max_w:
            x, y, row_h = 0.0, y - row_h - gap, 0.0
        offs.append((x, y - h))
        x += w + gap
        row_h = max(row_h, h)
    return offs


def render_step(pattern, seams, path: str, title: str = "") -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    inst = _instances(pattern, seams)
    rings, pieces = [], []
    for key, mir in inst:
        pc = pattern.piece(key)
        r = np.asarray(pc.seam_ring(), float).copy()
        if mir:
            r[:, 0] = -r[:, 0]
        rings.append(r)
        pieces.append((pc, mir))
    size = max(max(np.ptp(r[:, 0]), np.ptp(r[:, 1])) for r in rings)
    gap = 0.12 * size
    offs = _arrange(rings, gap)
    fig, ax = plt.subplots(figsize=(6.2, 3.3), dpi=80)
    for (pc, mir), r, (ox, oy) in zip(pieces, rings, offs):
        sh = np.array([ox - r[:, 0].min(), oy - r[:, 1].min()])
        rr = r + sh
        ax.fill(rr[:, 0], rr[:, 1], color=RIGHT_SIDE, ec="#444", lw=0.8, zorder=1)
        sign = -1.0 if mir else 1.0

        def tf(p, sign=sign, sh=sh):
            q = np.atleast_2d(np.asarray(p, float)).copy()
            q[:, 0] *= sign
            return q + sh

        for i, sm in enumerate(seams):
            col = COLORS[i % len(COLORS)]
            for side, ls in (("a", "-"), ("b", (0, (4, 1.5)))):
                for p, e, _n in sm[side]:
                    if p != pc.key:
                        continue
                    pts = tf(pc.edge(e).pts)
                    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=3.2, ls=ls, solid_capstyle="round", zorder=3)
                    for q, t, cnt in _notch_points(pc, e):
                        qq = tf(q)[0]
                        n = np.array([t[1], -t[0]]) * size * 0.035
                        n[0] *= sign
                        for k in range(cnt):
                            dd = np.array([t[0] * sign, t[1]]) * size * 0.012 * (k - (cnt - 1) / 2)
                            seg = np.array([qq + dd - n, qq + dd + n])
                            ax.plot(seg[:, 0], seg[:, 1], color="black", lw=1.2, zorder=4)
        c = rr.mean(axis=0)
        name = pc.name + (" (2nd piece)" if mir else "")
        ax.text(c[0], c[1], name, ha="center", va="center", fontsize=7, zorder=5,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
    handles = [Patch(fc=RIGHT_SIDE, ec="#444", label="right side of the fabric")]
    for i, sm in enumerate(seams):
        handles.append(Line2D([], [], color=COLORS[i % len(COLORS)], lw=3, label=sm["name"]))
    handles.append(Line2D([], [], color="black", lw=1.2, label="notches: match them"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=6.5,
              frameon=False)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=8, loc="left")
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=80)
    plt.close(fig)
    _shrink_png(path)
    return path


def _shrink_png(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB").quantize(colors=32)
        im.save(path, optimize=True)
    except Exception:  # pragma: no cover
        pass


def render_steps(pattern, steps: list[str], out_dir: str, sub: str = "steps") -> dict[int, str]:
    """Write one PNG per step that sews a seam; returns {step number (1-based): relative path}."""
    os.makedirs(os.path.join(out_dir, sub), exist_ok=True)
    res = {}
    for i, seams in enumerate(step_seams(pattern, steps), 1):
        if not seams:
            continue
        rel = f"{sub}/step_{i:02d}.png"
        render_step(pattern, seams, os.path.join(out_dir, rel), title=f"Step {i}")
        res[i] = rel
    return res
